import os
import logging
import moderngl
import yaml

from src.core import constants
from dataclasses import dataclass

@dataclass
class Shader:
    source_code_lines: list
    input_textures: list
    version: int
    varyings: list
    program: moderngl.Program


class ShaderLoader:

    def __init__(self, ctx: moderngl.Context, logger: logging.Logger = None):
        self.ctx = ctx
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.shaders = {}

    def load_shaders(self, directory: str) -> None:
        """
        Load and compile shaders from the given directory into programs.
        """

        # Load all shaders
        glsl_filenames = [filename for filename in os.listdir(directory) if filename.endswith('.glsl')]
        self.logger.info(f"Found {len(glsl_filenames)} shaders")

        # Load all extra definitions
        yaml_filenames = [filename for filename in os.listdir(directory) if filename.endswith('.yaml')]
        self.logger.info(f"Found {len(yaml_filenames)} yaml definition files")

        all_shader_extra_definitions = {}
        for filename in yaml_filenames:
            extra_definitions_fpath = os.path.join(directory, filename)
            with open(extra_definitions_fpath, 'r') as file:
                extra_definitions = yaml.safe_load(file)
                for shader_name, shader_definitions in extra_definitions.items():
                    if shader_name in all_shader_extra_definitions:
                        raise Exception(f"[ERROR] Shader definition for '{shader_name}' is repeated across "
                                        f"multiple YAML files.")
                    all_shader_extra_definitions[shader_name] = shader_definitions

        # The filename here marches the shader_name from all_shader_extra_definitions
        for filename in glsl_filenames:
            shader_fpath = os.path.join(directory, filename)
            with open(shader_fpath, 'r') as file:
                raw_source_code = file.read()
                self.shaders[filename] = self.create_shader(
                    raw_source_code=raw_source_code,
                    extra_definitions=all_shader_extra_definitions.get(filename, {}))

        # Compile all shaders
        for name, shader in self.shaders.items():
            if not self.compile_program(shader=shader):
                raise Exception(f"[ERROR] Failed to compile shader {name}. Check error description above")
            self.logger.info(f"Shader compiled: {name}")

    def create_shader(self, raw_source_code: str, extra_definitions: dict) -> Shader:
        """

        :param raw_source_code: str, all data from the text file as-is
        :return:
        """

        # Split raw code into lines but leave the new line at the end!
        code_lines = [line + "\n" for line in raw_source_code.splitlines()]

        # Get version - The final version will be the lowest version found!
        line_number_and_version_list = [(index, line) for index, line in enumerate(code_lines)
                                        if line.strip().startswith(constants.SHADER_LIBRARY_DIRECTIVE_VERSION)]

        recovered_versions = set([int(line[1].replace("#version", "").strip())
                                  for line in line_number_and_version_list])
        version = min(recovered_versions) if len(recovered_versions) > 0 else 0

        # Remove the line with the "#version"
        code_lines = [line for line in code_lines if not line.strip().startswith("#version")]

        # Find all expected input textures (uniform sampler2D)
        all_uniforms_lines = [line.lower().strip() for line in code_lines if line.lower().strip().startswith("uniform")]
        input_textures = []
        for uniform_line in all_uniforms_lines:
            parts = uniform_line.split()
            if len(parts) < 3:
                continue
            if parts[0] == "uniform" and parts[1] == "sampler2d":
                input_textures.append(parts[2].strip(";"))

        return Shader(
            source_code_lines=code_lines,
            input_textures=input_textures,
            version=version,
            varyings=extra_definitions.get("varyings", []),
            program=None)

    def compile_program(self, shader: Shader) -> bool:
        """
        Compile shaders into a program.
        """

        shader_names_in_order = ["vertex", "geometry", "fragment"]
        shader_sources = []

        try:
            for name in shader_names_in_order:
                shader_sources.append(
                    self.generate_shader_source_code(
                        code_lines=shader.source_code_lines,
                        version=shader.version,
                        shader_type=name))

            shader.program = self.ctx.program(
                vertex_shader=shader_sources[0],
                geometry_shader=shader_sources[1],
                fragment_shader=shader_sources[2],
                varyings=shader.varyings)

        except Exception as error:
            self.logger.error(f"Failed to compile program: {error}")
            return False
        return True

    def generate_shader_source_code(self,
                                    code_lines: list,
                                    version: int,
                                    shader_type: str,
                                    extra_definitions=None) -> str:

        if extra_definitions is None:
            extra_definitions = []

        # We need to check if there is code to be compiled for the type of shader. Othersize, return None
        matches = [line for line in code_lines if f"defined {shader_type.upper()}_SHADER" in line]
        if len(matches) == 0:
            return None

        header_lines = []
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_VERSION} {version}\n"]
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_DEFINE} {shader_type.upper()}_SHADER\n"]
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_DEFINE} {definition}\n"
                         for definition in extra_definitions]

        return "".join(header_lines + code_lines)

    def get_program(self, shader_filename: str) -> moderngl.Program:
        """
        Retrieve the compiled program by label.
        """
        return self.shaders[shader_filename].program