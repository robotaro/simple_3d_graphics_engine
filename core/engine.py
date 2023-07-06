import moderngl as mgl
from core import constants

from core.window import Window
from core.scene.scene import Scene


class Engine(Window):

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
        self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.main_scene = Scene(self)

        # Flags
        self._running = False

    def create_scene(self, name: str):

        pass

    def setup(self):

        self.main_scene.update()

    def render(self):

        self.context.clear(color=constants.BACKGROUND_COLOR_RGB)
        self.main_scene.render()

