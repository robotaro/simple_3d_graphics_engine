import os
from typing import Union
from dataclasses import dataclass
from core.utilities import utils_io


@dataclass
class Shader:
    label: str
    source_code_lines: list
    version: int
    contains_main: bool
    includes: list

class ShaderLibrary:

    """
    This class loads assemble the final code for all shaders in a specific folder.
    As GLSL does not support #imports, this class manages all the imports
    """

    def __init__(self, shader_directory: str):
        self.shader_directory = shader_directory
        self.shaders = {}
        self.load_shaders()

    def load_shaders(self):

        # Step 1) List all .glsl files in the directory
        relative_glsl_fpaths = utils_io.list_filepaths(directory=self.shader_directory, extension=".glsl")

        # Step 2) For each glsl filepath, create a new shader entry and loa its respective code
        for relative_fpath in relative_glsl_fpaths:

            new_shader = self._load_single_shader(relative_glsl_fpath=relative_fpath)
            if new_shader is None:
                continue

            self.shaders[new_shader.label] = new_shader

        # Step 3) Solve shader dependencies
        for key, shader in self.shaders.items():
            self._solve_shader_dependencies(shader_key=key)

    def _load_single_shader(self, relative_glsl_fpath: str):

        new_blueprint = None
        absolute_glsl_fpath = os.path.join(self.shader_directory, relative_glsl_fpath)
        with open(absolute_glsl_fpath, "r") as file:

            # All shader keys must be a relative path in Linux format
            label = relative_glsl_fpath.replace(os.sep, '/')

            # GLSL Source code
            code_lines = file.readlines()

            # Get version
            version_details = [(index, line) for index, line in enumerate(code_lines)
                               if line.strip().startswith("#version")]
            version = 0
            if len(version_details) > 0:
                version = int(version_details[0][1].replace("#version", "").strip())

            # Remove the line with the "#version"
            code_lines = [line for line in code_lines if not line.strip().startswith("#version")]

            # Contain mains
            contains_main = len([line for line in code_lines if "main()" in line]) > 0

            # Includes
            includes = [(index, line.replace("#include", "").strip()) for index, line in enumerate(code_lines)
                        if line.strip().startswith("#include")]

            # Sort includes in descending order
            includes_sorted_descending = sorted(includes, key=lambda x: x[0], reverse=True)

            new_blueprint = Shader(
                label=label,
                source_code_lines=code_lines,
                version=version,
                contains_main=contains_main,
                includes=includes_sorted_descending
            )

        return new_blueprint

    def _solve_shader_dependencies(self, shader_key: str) -> None:

        """
        This function replaces the "#include" directives with the respective code from another
        GSLS shader file
        :param shader_key: str, unique identifier used to represent a shader file in the directory
        :return: None (all data is modified in-place, in self.shaders)
        """

        if shader_key not in self.shaders:
            raise KeyError(f"[ERROR] Shader '{shader_key}' not present in the library")

        shader = self.shaders[shader_key]

        for (line_index, include_shader_key) in shader.includes:
            self._solve_shader_dependencies(shader_key=include_shader_key)

            # Replace include with code lines from dependency
            a = line_index
            b = line_index + 1
            shader.source_code_lines[a:b] = self.shaders[include_shader_key].source_code_lines

    def generate_source_code(self, shader_key: str, extra_definitions: Union[dict, None]=None) -> str:
        """
        This function assembles all lines of code, including the extra definitions, into a single
        string to be used for shader compilation later on. The version of the shader is added to the
        first line, and extra directives are added below, followed by the rest of the code

        example of extra_directives:

        {
            "VERTEX_SHADER": 1
            "PART_A": 0
        }

        turns into:

        #define VERTEX_SHADER 1
        #define PART_A 0

        :param shader_key: str, unique shader
        :param extra_definitions: dict, keys are the directive
        :return: str, source code
        """

        if extra_definitions is None:
            extra_definitions = {}

        shader = self.shaders[shader_key]

        version_line = f"#version {shader.version}\n"
        directive_lines = [f"#define {key} {value}\n" for key, value in extra_definitions.items()]
        header_lines = [version_line] + directive_lines

        return "".join(header_lines + shader.source_code_lines)
