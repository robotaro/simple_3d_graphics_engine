import pygame as pg
import moderngl as mgl
from core import constants
import sys
import time
from core.scene import Scene


class Engine:

    def __init__(self, window_size=constants.WINDOW_SIZE):

        self.window_size = window_size
        pg.init()

        # Initialise Window (PyGame)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, constants.OPENGL_MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, constants.OPENGL_MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode(self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)

        # Setup drawing context (ModernGL)
        self.context = mgl.create_context()
        self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.main_scene = Scene(self)

    def create_vbo(self, name: str):

        pass

    def render(self):

        # Clear framebuffer
        self.context.clear(color=constants.BACKGROUND_COLOR_RGB)

        self.main_scene.render()

        # Swap buffers
        pg.display.flip()

    def _process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):

                pg.quit()
                sys.exit()

    def run(self):

        previous_time = time.perf_counter()
        while True:
            self._process_events()
            self.render()
