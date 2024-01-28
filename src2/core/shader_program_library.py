import logging
import os
from typing import Union
from dataclasses import dataclass
import yaml
import moderngl

from src.core import constants
from src.utilities import utils_io


@dataclass
class ShaderBlueprint:
    """
    The blueprint will contain source code for all types of shader. But each is activated when you generate
    the final source code for each type. This will add a directive "#define" with the type of shader being used
    """
    label: str
    source_code_lines: list
    input_textures: list
    version: int
    contains_main: bool
    includes: list


@dataclass
class ProgramBlueprint:
    label: str
    vertex_shader: str
    fragment_shader: str
    geometry_shader: str
    varyings: list
    input_texture_locations: dict
    extra_definitions: dict  # TODO Check this


class ShaderProgramLibrary:

    """
    This class loads assemble the final code for all shaders in a specific folder.
    As GLSL does not support #imports, this class manages all the imports
    """

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_directory=constants.SHADERS_DIR,
                 shader_programs_yaml_fpath="",
                 logger: Union[logging.Logger, None]=None):

        # Input variables
        self.ctx = ctx
        self.logger = logger if logger is not None else logging.Logger
        self.shader_directory = shader_directory
        self.shader_programs_yaml_fpath = shader_programs_yaml_fpath

        # Core variables
        self.shader_blueprints = {}
        self.program_blueprints = {}
        self.programs = {}

        # Initialise in the constructor, for simplicity
        self.load_shaders()
        self.compile_programs()

    def __getitem__(self, program_id: str):
        if program_id not in self.programs:
            raise KeyError(f"[ERROR] Program ID '{program_id}' is not present in the program library")
        return self.programs.get(program_id, None)

    def load_shaders(self) -> None:
        """
        This is a rather general function that loads all shader files and program definitions located in the
        same directory. Once those are loaded, shader blueprints and program blueprints are created, and the
        final source code for the shaders can be compiled into each program listed in the YAML file
        :return:
        """

        # Step 1) Create shader blueprints from the GLSL files
        relative_glsl_fpaths = utils_io.list_filepaths(directory=self.shader_directory,
                                                       extension=constants.SHADER_LIBRARY_FILE_EXTENSION)
        for relative_fpath in relative_glsl_fpaths:

            new_shader_blueprint = self.create_shader_blueprint(relative_glsl_fpath=relative_fpath)
            if new_shader_blueprint is None:
                continue

            self.shader_blueprints[new_shader_blueprint.label] = new_shader_blueprint

        # Step 2) Solve shader dependencies AFTER all shaders have been loaded (who includes who and whatnot)
        for key, shader in self.shader_blueprints.items():
            self._solve_shader_dependencies(shader_key=key)

        # Step 3) Create program blueprints from the YAML files - but in this case, there are many de
        relative_yaml_fpaths = utils_io.list_filepaths(directory=self.shader_directory,
                                                       extension=constants.SHADER_LIBRARY_PROGRAM_DEFINITION_EXTENSION)
        for relative_fpath in relative_yaml_fpaths:

            program_definitions = None
            fpath = os.path.join(self.shader_directory, relative_fpath)
            with open(fpath, 'r') as file:
                program_definitions = yaml.safe_load(file)

            for program_label, program_definition in program_definitions.items():
                new_program_blueprint = self.create_program_blueprint(
                    program_definition=program_definition,
                    label=program_label)
                if new_program_blueprint is None:
                    continue

                self.program_blueprints[program_label] = new_program_blueprint

    def shutdown(self):
        # After removing the vao release stage from all other parts of the pipeline, add them here

        pass

    # =========================================================================
    #                           Internal Functions
    # =========================================================================

    def create_program_blueprint(self, program_definition: dict, label: str):
        return ProgramBlueprint(
            label=label,
            vertex_shader=program_definition.get("vertex_shader", None),
            fragment_shader=program_definition.get("fragment_shader", None),
            geometry_shader=program_definition.get("geometry_shader", None),
            varyings=program_definition.get(constants.SHADER_LIBRARY_YAML_KEY_VARYINGS, []),
            input_texture_locations=program_definition.get(
                constants.SHADER_LIBRARY_YAML_KEY_INPUT_TEXTURE_LOCATIONS, {}),
            extra_definitions=program_definition.get(constants.SHADER_LIBRARY_YAML_KEY_EXTRA_DEFINITIONS, {}))

    def create_shader_blueprint(self, relative_glsl_fpath: str) -> ShaderBlueprint:

        new_blueprint = None
        absolute_glsl_fpath = os.path.join(self.shader_directory, relative_glsl_fpath)
        with open(absolute_glsl_fpath, "r") as file:

            # All shader keys must be a relative path in Linux format
            label = relative_glsl_fpath.replace(os.sep, '/')

            # GLSL Source code
            code_lines = file.readlines()

            # Get version - The final version will be the lowest version found!
            line_number_and_version_list = [(index, line) for index, line in enumerate(code_lines)
                                            if line.strip().startswith(constants.SHADER_LIBRARY_DIRECTIVE_VERSION)]

            recovered_versions = set([int(line[1].replace("#version", "").strip())
                                  for line in line_number_and_version_list])
            version = min(recovered_versions) if len(recovered_versions) > 0 else 0

            # Remove the line with the "#version"
            code_lines = [line for line in code_lines if not line.strip().startswith("#version")]

            # Contain mains
            contains_main = len([line for line in code_lines if "main()" in line]) > 0

            # Find all expected input textures (uniform sampler2D)
            all_uniforms_lines = [line.lower().strip() for line in code_lines if line.lower().strip().startswith("uniform")]
            input_textures = []
            for uniform_line in all_uniforms_lines:
                parts = uniform_line.split()
                if len(parts) < 3:
                    continue
                if parts[0] == "uniform" and parts[1] == "sampler2d":
                    input_textures.append(parts[2].strip(";"))

            # Includes
            includes = [(index, line.replace("#include", "").strip()) for index, line in enumerate(code_lines)
                        if line.strip().startswith("#include")]

            # Sort includes in descending order
            includes_sorted_descending = sorted(includes, key=lambda x: x[0], reverse=True)

            new_blueprint = ShaderBlueprint(
                label=label,
                source_code_lines=code_lines,
                input_textures=input_textures,
                version=version,
                contains_main=contains_main,
                includes=includes_sorted_descending
            )

        return new_blueprint

    def compile_programs(self):
        """
        A program is compiled from a program blueprint, stored in the YAML file. The program blueprint requires
        shader blueprints, created from a GLSL file.

        Compiles all programs defined in the YAML definition file. The programs are compiled according to the
        definitions from the YAML file, not purely based on their GLSL code. This gives us the flexibility to
        tailor them to different usages.

        :return: list, List of dictionaries containing the shader
                 program that failed and its respective description
        """

        # If no YAML file has been specified, look for one in the shader directory
        if len(self.program_blueprints) == 0:
            raise Exception("[ERROR] There are no programs to be compiled. Please load their definitions form a .yaml file.")

        # Compile each program according to their loaded shader blueprint
        # (from GSLS) and their program definitions (from YAML)
        for program_label, program_blueprint in self.program_blueprints.items():

            vertex_blueprint = self.shader_blueprints.get(program_blueprint.vertex_shader, None)
            vertex_source = self.generate_shader_source_code(
                program_blueprint=program_blueprint,
                shader_blueprint=vertex_blueprint,
                shader_type=constants.SHADER_TYPE_VERTEX)

            geometry_blueprint = self.shader_blueprints.get(program_blueprint.geometry_shader, None)
            geometry_source = self.generate_shader_source_code(
                program_blueprint=program_blueprint,
                shader_blueprint=geometry_blueprint,
                shader_type=constants.SHADER_TYPE_GEOMETRY)

            fragment_blueprint = self.shader_blueprints.get(program_blueprint.fragment_shader, None)
            fragment_source = self.generate_shader_source_code(
                program_blueprint=program_blueprint,
                shader_blueprint=fragment_blueprint,
                shader_type=constants.SHADER_TYPE_FRAGMENT)

            # TODO: Think of a more reliable way to ensure all textures are used
            self.check_if_all_shader_texture_locations_are_used(
                program_blueprint=program_blueprint,
                shader_blueprint=fragment_blueprint)

            try:
                # Compile the program
                program = self.ctx.program(
                    vertex_shader=vertex_source,
                    geometry_shader=geometry_source,
                    fragment_shader=fragment_source,
                    varyings=program_blueprint.varyings)

                # Assign uniform sampler2d locations, if defined
                for sampler_name, sampler_location in program_blueprint.input_texture_locations.items():

                    if not isinstance(sampler_location, int):
                        raise Exception("[ERROR] Uniform Sampler2D location should be of type 'int'")

                    if sampler_name not in program:
                        raise Exception(f"[ERROR] Sampler '{sampler_name}' not declared in shader")

                    program[sampler_name].value = sampler_location

            except Exception as error:
                # TODO: Sort out how you want this
                raise Exception(f"[ERROR] Program '{program_label}' did not compile. "
                                f"Here are the errors:\n\n[{program_label}]\n\n{error.args[0]}")

            self.programs[program_label] = program

    def check_if_all_shader_texture_locations_are_used(self,
                                                       program_blueprint: ProgramBlueprint,
                                                       shader_blueprint: ShaderBlueprint) -> bool:
        """
        This function checks if every input texture originally declared in the .glsl file is being used by its
        respective program. Granted, there will be EDGE CASES where the extra_definitions may disable some textures,
        but most cases will be covered. This only raises a warning because of those edge cases.

        # TODO: Consider the case where a program blueprint may use different shader blueprints, like taking the vertex
        #       shader from one and the fragment shader from another.

        :param program_blueprint: input program blueprint
        :param shader_blueprint: input shader blueprint (it mai contain
        :return:
        """
        if shader_blueprint is None:
            return False

        all_locations_present = True
        for input_texture in shader_blueprint.input_textures:
            if input_texture not in program_blueprint.input_texture_locations:
                self.logger.warning(f"[WARNING] Input texture '{input_texture}' from shader "
                                    f"'{shader_blueprint.label}' not present in program '{program_blueprint.label}'. "
                                    f"Please make sure to add this definition to the YAML file, under "
                                    f"{constants.SHADER_LIBRARY_YAML_KEY_INPUT_TEXTURE_LOCATIONS} section of the "
                                    f"respective program")
                all_locations_present = False
        return all_locations_present

    def generate_shader_source_code(self,
                                    program_blueprint: ProgramBlueprint,
                                    shader_blueprint: ShaderBlueprint,
                                    shader_type: str) -> Union[str, None]:

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

        if shader_blueprint is None:
            return None

        header_lines = []
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_VERSION} {shader_blueprint.version}\n"]
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_DEFINE} {shader_type.upper()}_SHADER\n"]
        header_lines += [f"{constants.SHADER_LIBRARY_DIRECTIVE_DEFINE} {definition}\n" for definition in
                         program_blueprint.extra_definitions]

        return "".join(header_lines + shader_blueprint.source_code_lines)

    def _solve_shader_dependencies(self, shader_key: str) -> None:

        """
        This function replaces the "#include" directives with the respective code from another blueprint.
        This is effectivelly inserting the code from one GSLS shader file into another :)

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
