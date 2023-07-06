from core import constants
import moderngl
from typing import Union


class Shader:

    def __init__(self, context: moderngl.Context, macro_definitions: Union[None, dict] = None):
        self.context = context
        self.program = None
        self.shader_code_lines = []
        self.macro_definitions = macro_definitions if macro_definitions is not None else {}

    def load(self, glsl_fpath: str) -> bool:

        # Load shader code as invididual lines
        with open(glsl_fpath, "r") as file:
            self.shader_code_lines = file.read()

    def compile(self):

        # Generate versions of the code for each
        vertex_shader = self.shader_code

        #self.program = self.context.program(
        #    vertex_shader=vertex_shader,
        #    fragment_shader=fragment_shader,
        #    geometry_shader=
        #)

    def destroy(self):
        if self.program is not None:
            self.program.release()

# DEBUG
loader = ShaderLibrary(mgl_context=None)
loader.load_shaders(directory=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\shaders")