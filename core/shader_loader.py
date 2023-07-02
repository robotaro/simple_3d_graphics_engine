from core import constants
import moderngl


class ShaderLoader:

    """
    This class loads and compiles all shaders located in the "shaders" folder.

    Shaders are loaded into a dictionary, where the key is their relative filepath
    inside the "shaders" folder. You can define the fragment, geometry and vertex
    shaders inside the same shader file by using MACROs that are activated when
    compiling the file.

    """

    def __init__(self, mgl_context, shader_program_name: str):
        self.mgl_context = mgl_context
        with open(f'shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()



    def load_shaders(self, directory: str, recursively=True) -> dict:




        self.program = self.mgl_context.program(vertex_shader=vertex_shader,
                                                fragment_shader=fragment_shader)

    def destroy(self):
        self.program.release()

