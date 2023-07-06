import os
import re
from dataclasses import dataclass
from core.utilities import utils_io


@dataclass
class Shader:
    label: str
    source_code: str
    source_code_lines: list
    version: int
    version_directive_line_index: int
    contains_main: bool
    includes: list


class ShaderLibrary:

    def __init__(self, shader_directory: str):
        self.shader_directory = shader_directory
        self.shaders = {}

    def load_shaders(self):

        # Step 1) List all .glsl files in the directory
        relative_glsl_fpaths = utils_io.list_filepaths(directory=self.shader_directory, extension=".glsl")

        # Step 2) For each glsl filepath, create a new shader entry and loa its respective code
        for relative_fpath in relative_glsl_fpaths:

            new_shader = self.load_shader(relative_glsl_fpath=relative_fpath)
            self.shaders[new_shader.label] = new_shader

        # Step 3) Assemble source code based on shader's include structures
        for key, shader in self.shaders.items():
            self.solve_shader_dependencies(shader_key=key)

        # TODO:
        # 1) Remove version directive from code lines
        # 2)

    def load_shader(self, relative_glsl_fpath: str):

        new_blueprint = None
        absolute_glsl_fpath = os.path.join(self.shader_directory, relative_glsl_fpath)
        with open(absolute_glsl_fpath, "r") as file:

            # All shader keys must be a relative path in Linux format
            label = relative_glsl_fpath.replace(os.sep, '/')

            # GLSL Source code
            code_lines = file.readlines()

            # Version
            version_details = [(index, line) for index, line in enumerate(code_lines)
                               if line.strip().startswith("#version")]
            version_directive_line_index = -1
            version = 0
            if len(version_details) > 0:
                version = int(version_details[0][1].replace("#version", "").strip())

            # Contain mains
            contains_main = len([line for line in code_lines if "main()" in line]) > 0

            # Includes
            includes = [(index, line.replace("#include", "").strip()) for index, line in enumerate(code_lines)
                        if line.strip().startswith("#include")]

            # Sort includes in descending order
            includes_sorted_descending = sorted(includes, key=lambda x: x[0], reverse=True)

            new_blueprint = Shader(
                label=label,
                source_code="",  # Not ready yet
                source_code_lines=code_lines,
                version=version,
                version_directive_line_index=version_directive_line_index,
                contains_main=contains_main,
                includes=includes_sorted_descending
            )

        return new_blueprint

    def solve_shader_dependencies(self, shader_key: str) -> None:

        """
        This function replaces the "#include" directives with the respective code from another
        GSLS shader file
        :param shader_key: str, unique identifier used to represent a shader file in the directory
        :return: None (all data is modified in-place, in self.shaders)
        """

        if shader_key not in self.shaders:
            raise KeyError(f"[ERROR] Shader '{shader_key}' not present in the library")

        shader = self.shaders[shader_key]

        # If shader source code has already been assembled, there is nothing else to do
        if len(shader.source_code) > 0:
            return

        for (line_index, include_shader_key) in shader.includes:
            self.solve_shader_dependencies(shader_key=include_shader_key)

            # Replace include with code lines from dependency
            a = line_index
            b = a + 1
            shader.source_code_lines[a:b] = self.shaders[include_shader_key].source_code_lines

        # Once all dependencies are handled, you can now assemblye the GLSL source code :)
        print(f'Source code assembled: {shader_key}')
        shader.source_code = "".join(shader.source_code_lines)


library = ShaderLibrary(shader_directory=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\shaders")
library.load_shaders()