import os
import logging
import moderngl

from src.core import constants
from dataclasses import dataclass

@dataclass
class Shader:
    source_code_lines: list
    input_textures: list
    version: int
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
        for filename in glsl_filenames:

            shader_fpath = os.path.join(directory, filename)

            with open(shader_fpath, 'r') as file:
                raw_source_code = file.read()
                self.shaders[filename] = self.create_shader(raw_source_code=raw_source_code)
                self.logger.info(f"Shader found: {filename}")

        # Compile all shaders
        for name, shader in self.shaders.items():
            self.logger.info(f"Compiling shader: {name}")
            self.compile_program(shader=shader)
            g = 0


    def create_shader(self, raw_source_code) -> Shader:
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
            program=None)

    def compile_program(self, shader: Shader) -> None:
        """
        Compile shaders into a program.
        """

        try:
            vertex_source = self.generate_shader_source_code(
                code_lines=shader.source_code_lines,
                version=shader.version,
                shader_type="vertex"
            )
            geometry_source = self.generate_shader_source_code(
                code_lines=shader.source_code_lines,
                version=shader.version,
                shader_type="geometry"
            )
            fragment_source = self.generate_shader_source_code(
                code_lines=shader.source_code_lines,
                version=shader.version,
                shader_type="fragment"
            )

            shader.program = self.ctx.program(
                vertex_shader=vertex_source,
                geometry_shader=geometry_source,
                fragment_shader=fragment_source
            )

            self.logger.info("Program compiled successfully")
        except Exception as error:
            self.logger.error(f"Failed to compile program: {error}")

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


# Example usage
if __name__ == '__main__':
    import moderngl
    ctx = moderngl.create_standalone_context()

    shader_loader = ShaderLoader(ctx)
    shader_loader.load_shaders(r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\src3\shaders")

    # Retrieve a compiled shader
    vertex_shader = shader_loader.get_shader('vertex_shader.glsl')
    fragment_shader = shader_loader.get_shader('fragment_shader.glsl')