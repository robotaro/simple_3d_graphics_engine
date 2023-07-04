from core import constants
import moderngl

from core.utilities import utils_files


class ShaderLibrary:

    """
    This class loads and compiles all shaders located in the "shaders" folder.

    Shaders are loaded into a dictionary, where the key is their relative filepath
    inside the "shaders" folder. You can define the fragment, geometry and vertex
    shaders inside the same shader file by using MACROs that are activated when
    compiling the file.

    """

    def __init__(self, mgl_context: moderngl.Context):
        self.mgl_context = mgl_context

    def load_shaders(self, directory: str, recursively=True) -> dict:

        shaders = {}

        filenames = utils_files.list_filenames(directory=directory)

        self.program = self.mgl_context.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader)

    def destroy(self):
        self.program.release()

# DEBUG
loader = ShaderLibrary(mgl_context=None)
loader.load_shaders(directory=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\shaders")