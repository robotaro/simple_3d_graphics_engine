import numpy as np
from core import constants as constants

import glfw
import imgui
from core.window.window_glfw import WindowGLFW



class WindowGLFWImGUI(WindowGLFW):
    
    __slots__ = ('window_size',
                 'window_title',
                 'vertical_sync',
                 'mouse_state',
                 'keyboard_state',
                 'window_glfw',
                 'context',
                 'imgui_renderer')
    
    # ========================================================================
    #                          Initialization functions
    # ========================================================================

    def __init__(self,
                 window_size=constants.WINDOW_DEFAULT_SIZE,
                 window_title=constants.WINDOW_DEFAULT_TITLE,
                 vertical_sync=False):

        super().__init__(
            window_size=window_size,
            window_title=window_title,
            vertical_sync=vertical_sync)

    
    # ========================================================================
    #                       Input Callback functions
    # ========================================================================


    def _glfw_callback_mouse_button(self, glfw_window, button, action, mods):
        super()._glfw_callback_mouse_button(
            glfw_window=glfw_window,
            button=button,
            action=action,
            mods=mods)

    def _glfw_callback_mouse_move(self, glfw_window, x, y):
        self.imgui_renderer.mouse_callback(glfw_window, x, y)
        self.mouse_state[constants.MOUSE_POSITION] = (x, y)

    def _glfw_callback_mouse_scroll(self, glfw_window, x_offset, y_offset):
        self.imgui_renderer.scroll_callback(glfw_window, x_offset, y_offset)
        self.mouse_state[constants.MOUSE_SCROLL_POSITION] += y_offset

    def _glfw_callback_window_resize(self, glfw_window, width, height):
        self.imgui_renderer.resize_callback(glfw_window, width, height)

    # ========================================================================
    #                              Main Loop
    # ========================================================================

    def run(self):

        self.setup()
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window_glfw)

        while not glfw.window_should_close(self.window_glfw):

            glfw.poll_events()
            self.imgui_renderer.process_inputs()

            self._update_inputs()

            self.context.clear(0.0, 0.0, 0.0)
            self.render()

            imgui.render()
            self.imgui_renderer.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window_glfw)

        self.imgui_renderer.shutdown()
        glfw.terminate()
