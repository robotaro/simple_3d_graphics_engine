import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer


class CustomGlfwRenderer(GlfwRenderer):
    def __init__(self, window, attach_callbacks: bool = True):
        super().__init__(window, attach_callbacks)
        self.cursor_hidden = False

    def hide_cursor(self):
        self.cursor_hidden = True
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def show_cursor(self):
        self.cursor_hidden = False
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def process_inputs(self):

        def compute_fb_scale(window_size, fb_size):
            return (
                fb_size[0] / window_size[0] if window_size[0] > 0 else 0,
                fb_size[1] / window_size[1] if window_size[1] > 0 else 0,
            )

        io = imgui.get_io()

        window_size = glfw.get_window_size(self.window)
        fb_size = glfw.get_framebuffer_size(self.window)

        io.display_size = window_size
        io.display_fb_scale = compute_fb_scale(window_size, fb_size)
        io.delta_time = 1.0 / 60

        if glfw.get_window_attrib(self.window, glfw.FOCUSED):
            # Only update mouse position if cursor is not hidden
            if not self.cursor_hidden:
                io.mouse_pos = glfw.get_cursor_pos(self.window)
            else:
                io.mouse_pos = -1, -1
        else:
            io.mouse_pos = -1, -1

        io.mouse_down[0] = glfw.get_mouse_button(self.window, 0)
        io.mouse_down[1] = glfw.get_mouse_button(self.window, 1)
        io.mouse_down[2] = glfw.get_mouse_button(self.window, 2)

        current_time = glfw.get_time()

        if self._gui_time:
            self.io.delta_time = current_time - self._gui_time
        else:
            self.io.delta_time = 1. / 60.
        if(io.delta_time <= 0.0): io.delta_time = 1./ 1000.

        self._gui_time = current_time


