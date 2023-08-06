import os
from typing import Union
from dataclasses import dataclass
import yaml
import moderngl

from core import constants
from core.utilities import utils_io


@dataclass
class ShaderBlueprint:
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

    def __init__(self,
                 context: moderngl.Context,
                 shader_directory=constants.SHADERS_DIRECTORY,
                 shader_programs_config_fpath=constants.SHADER_PROGRAMS_YAML_FPATH):

        # Input variables
        self.context = context
        self.shader_programs_config_fpath = shader_programs_config_fpath
        self.shader_directory = shader_directory

        # Core variables
        self.shader_blueprints = {}
        self.programs = {}

        self.load_shaders()

        self.compile_programs()

    def __getitem__(self, program_id: str):
        if program_id not in self.programs:
            raise KeyError(f"[ERROR] Program ID '{program_id}' is not present in the program library")
        return self.programs.get(program_id, None)

    def load_shaders(self) -> None:

        # Step 1) List all .glsl files in the directory
        relative_glsl_fpaths = utils_io.list_filepaths(directory=self.shader_directory, extension=".glsl")

        # Step 2) For each glsl filepath, create a new shader entry and loa its respective code
        for relative_fpath in relative_glsl_fpaths:

            new_shader = self._load_shader_file(relative_glsl_fpath=relative_fpath)
            if new_shader is None:
                continue

            self.shader_blueprints[new_shader.label] = new_shader

        # Step 3) Solve shader dependencies
        for key, shader in self.shader_blueprints.items():
            self._solve_shader_dependencies(shader_key=key)

    def print_compilation_results(self):

        print("[ Compilation Results ]")
        for key, program_entry in self.programs.items():
            errors = program_entry["compilation_errors"]
            successful = len(errors) == 0
            result = "Compiled" if successful else "Failed"
            print(f" > {key}: {result}")
            if not successful:
                print(errors)
                print("\n")

    # =========================================================================
    #                           Internal Functions
    # =========================================================================

    def _load_shader_file(self, relative_glsl_fpath: str):

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

            new_blueprint = ShaderBlueprint(
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

        if shader_key not in self.shader_blueprints:
            raise KeyError(f"[ERROR] Shader '{shader_key}' not present in the library")

        shader = self.shader_blueprints[shader_key]

        for (line_index, include_shader_key) in shader.includes:
            self._solve_shader_dependencies(shader_key=include_shader_key)

            # Replace include with code lines from dependency
            a = line_index
            b = line_index + 1
            shader.source_code_lines[a:b] = self.shader_blueprints[include_shader_key].source_code_lines

    def _blueprint2source_code(self, blueprint: dict, shader_type: str) -> Union[str, None]:

        extra_definitions = blueprint.get("extra_definitions", {})

        source = None
        blueprint_key = f"{shader_type}_shader"
        if blueprint_key in blueprint:
            shader_name = blueprint[blueprint_key]
            if shader_name not in self.shader_blueprints:
                raise KeyError(f"[ERROR] Shader '{shader_name}' not found in shader library")
            source = self._generate_source_code(
                shader_key=shader_name,
                shader_type=shader_type,
                extra_definitions=extra_definitions)

        return source

    def _generate_source_code(self,
                              shader_key: str,
                              shader_type: str,
                              extra_definitions: Union[dict, None]=None) -> str:
        """
        This function assembles all lines of code, including the extra definitions, into a single
        string to be used for shader compilation later on. The version of the shader is added to the
        first line, and extra directives are added below, followed by the rest of the code.

        [IMPORTANT] Extra definitions and shader type strings will be used in UPPER CASE! Please
                    make sure that your GLSL code matches the UPPER CASE version of your variables!

        Example of shader type:

        shader_type = "fragment"

        turns into:

        #define FRAGMENT_SHADER

        Example of extra_directives:

        {
            "VERTEX_SHADER": 1
            "PART_A": 0
        }

        turns into:

        #define VERTEX_SHADER 1
        #define PART_A 0

        :param shader_key: str, unique shader
        :param shader_type: str, one of the valid types of shader. This directive is used to select the
                            right part of the GLSL code to be compiled.
        :param extra_definitions: dict, keys are the directive
        :return: str, source code
        """

        if shader_type not in constants.SHADER_TYPES:
            raise ValueError(f"[ERROR] Shader type '{shader_type}' not supported. "
                             f"Shader type must be one of the following: {constants.SHADER_TYPES}")

        if extra_definitions is None:
            extra_definitions = {}

        shader = self.shader_blueprints[shader_key]

        header_lines = []
        header_lines += [f"#version {shader.version}\n"]
        header_lines += [f"#define {shader_type.upper()}_SHADER\n"]
        header_lines += [f"#define {key.upper()} {value}\n" for key, value in extra_definitions.items()]

        return "".join(header_lines + shader.source_code_lines)

    def compile_programs(self):
        """
        Compiles all programs defined in the YAML definition file. The programs

        :return: list, List of dictionaries containing the shader
                 program that failed and its respective description
        """

        yaml_dict = None
        with open(self.shader_programs_config_fpath, 'r') as file:
            yaml_dict = yaml.safe_load(file)

        if yaml_dict is None:
            yaml_dict = {}

        for key, blueprint in yaml_dict.items():

            # Generate source code for all individual shaders that will make the final program
            vertex_source = self._blueprint2source_code(shader_type="vertex", blueprint=blueprint)
            geometry_source = self._blueprint2source_code(shader_type="geometry", blueprint=blueprint)
            fragment_source = self._blueprint2source_code(shader_type="fragment", blueprint=blueprint)

            # Compile the program
            try:
                compiled_program = self.context.program(
                    vertex_shader=vertex_source,
                    geometry_shader=geometry_source,
                    fragment_shader=fragment_source)

            except Exception as error:
                # TODO: Sort out how you want this
                raise Exception(f"[ERROR] Program '{key}' did not compile. "
                                f"Here are the errors:\n\n[{key}]\n\n{error.args[0]}")

            self.programs[key] = compiled_program




