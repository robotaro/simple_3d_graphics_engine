import moderngl as mgl
from core import constants
import sys
import time

from core.window_glfw import WindowGLFW
from core.scene import Scene


class Engine(WindowGLFW):

    def __init__(self, 
                 window_size=constants.WINDOW_DEFAULT_SIZE,
                 window_title=constants.WINDOW_DEFAULT_TITLE,
                 vertical_sync=False):

        # Window is created here
        super().__init__(
            window_size=window_size,
            window_title=window_title,
            vertical_sync=vertical_sync)

        # OpenGL context must be created after the window
        self.context = mgl.create_context()
        self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.main_scene = Scene(self)

        # Flags
        self._running = False


    def create_vbo(self, name: str):

        pass

    def callback_setup(self):

        self.main_scene.update()

    def callback_render(self):

        self.context.clear(color=constants.BACKGROUND_COLOR_RGB)
        self.main_scene.render()

