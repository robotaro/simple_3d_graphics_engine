import pygame as pg
import moderngl as mgl
from core import constants


class Engine:

    def __init__(self, window_size=constants.WINDOW_SIZE):

        self.window_size = window_size
        pg.init()

        # Initialise Window (PyGame)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, constants.OPENGL_MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, constants.OPENGL_MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode(self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)

        # Setup drawing context (ModerlGL)
        self.context = mgl.create_context()
        self.context.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)



    def render(self):

        pass

    def _Update(self):

        pass

    def run(self):
        pass
