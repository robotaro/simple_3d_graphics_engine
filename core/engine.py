import moderngl as mgl
from core import constants
import sys
import time

from core.window_glfw import WindowGLFW
from core.scene import Scene


class Engine:

    def __init__(self, window_size=constants.WINDOW_DEFAULT_SIZE):

        self.window = WindowGLFW(window_size=window_size)

        # Setup drawing context (ModernGL)
        self.context = mgl.create_context()
        self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.main_scene = Scene(self)

        # Flags
        self._running = False

    def create_vbo(self, name: str):

        pass

    def update(self):

        self.main_scene.update()

    def render(self):

        # Clear framebuffer
        self.context.clear(color=constants.BACKGROUND_COLOR_RGB)

        self.main_scene.render()

        # Swap buffers
        pg.display.flip()

    def run(self):

        # Create window here

        previous_time = time.perf_counter()
        while self._running:

            self.update()
            self.render()
