
from src3.shader_loader import ShaderLoader
from src3.window_glfw import WindowGLFW
from src.utilities import utils_logging


class Editor(WindowGLFW):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = utils_logging.get_project_logger(project_logger_name="Editor")
        self.shader_loader = ShaderLoader(logger=self.logger, ctx=self.ctx)

    def initialise(self):
        SHADERS_DIRECTORY = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\src3\shaders"
        self.shader_loader.load_shaders(directory=SHADERS_DIRECTORY)

    def update(self):
        pass

    def shutdown(self):
        pass