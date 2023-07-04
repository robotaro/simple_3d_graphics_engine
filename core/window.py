# Core modules
import numpy as np
from core import constants

# Graphics
import glfw
import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer


class Window:

    """
    The Window class is a GLFW wrapper around the GLFW module to simplify development.
    In addition, ImGUI has been integrated to provide expeditious testing debugging.
    A window is created when the constructor is called and should be utilised as:

    """
    
    __slots__ = ("window_size",
                 "window_title",
                 "vertical_sync",
                 "mouse_state",
                 "keyboard_state",
                 "window_glfw",
                 "context",
                 "imgui_renderer")
    
    # ========================================================================
    #                          Initialization functions
    # ========================================================================

    def __init__(self,
                 window_size=constants.WINDOW_DEFAULT_SIZE,
                 window_title=constants.WINDOW_DEFAULT_TITLE,
                 vertical_sync=False):

        # ModernGL variables
        self.window_size = window_size
        self.window_title = window_title
        self.vertical_sync = vertical_sync

        # Input variables
        self.mouse_state = self.initialise_mouse_state()
        self.keyboard_state = self.initialise_keyboard_state()

        if not glfw.init():
            raise ValueError("[ERROR] Failed to initialize GLFW")

        # TODO: Find out about samples hint before creating the window
        glfw.window_hint(glfw.SAMPLES, 4)

        self.window_glfw = glfw.create_window(width=self.window_size[0],
                                              height=self.window_size[1],
                                              title=window_title,
                                              monitor=None,
                                              share=None)

        # Create a windowed mode window and its OpenGL context
        if not self.window_glfw:
            glfw.terminate()
            raise Exception('[ERROR] Could not create GLFW window.')

        glfw.make_context_current(self.window_glfw)
        glfw.swap_interval(1 if self.vertical_sync else 0)

        self.context = moderngl.create_context()

        # Assign callback functions
        glfw.set_key_callback(self.window_glfw, self._glfw_callback_keyboard)
        glfw.set_char_callback(self.window_glfw, self._glfw_callback_char)
        glfw.set_cursor_pos_callback(self.window_glfw, self._glfw_callback_mouse_move)
        glfw.set_mouse_button_callback(self.window_glfw, self._glfw_callback_mouse_button)
        glfw.set_window_size_callback(self.window_glfw, self._glfw_callback_window_resize)
        glfw.set_scroll_callback(self.window_glfw, self._glfw_callback_mouse_scroll)
        glfw.set_framebuffer_size_callback(self.window_glfw, self._glfw_callback_framebuffer_size)
        glfw.set_drop_callback(self.window_glfw, self._glfw_callback_drop_files)
        
        # Update any initialisation variables after window GLFW has been created, if needed
        self.mouse_state[constants.MOUSE_POSITION] = glfw.get_cursor_pos(self.window_glfw)

        # ImGUI variables
        self.imgui_renderer = None

    # ========================================================================
    #                           Input State Functions
    # ========================================================================

    def initialise_mouse_state(self) -> dict:
        return {
            constants.MOUSE_LEFT: constants.BUTTON_UP,
            constants.MOUSE_RIGHT: constants.BUTTON_UP,
            constants.MOUSE_MIDDLE: constants.BUTTON_UP,
            constants.MOUSE_POSITION: (0, 0),
            constants.MOUSE_POSITION_LAST_FRAME: (0, 0),
            constants.MOUSE_SCROLL_POSITION: 0
        }
        
    def initialise_keyboard_state(self) -> np.array:
        return np.ones((constants.KEYBOARD_SIZE,), dtype=np.int8) * constants.KEY_STATE_UP
    
    # ========================================================================
    #                       GLFW Callback functions
    # ========================================================================

    def _glfw_callback_char(self, glfw_window, char):
        self.imgui_renderer.char_callback(window=glfw_window, char=char)

    def _glfw_callback_keyboard(self, glfw_window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keyboard_state[key] = constants.KEY_STATE_DOWN
        if action == glfw.RELEASE:
            self.keyboard_state[key] = constants.KEY_STATE_UP

        self.imgui_renderer.keyboard_callback(glfw_window, key, scancode, action, mods)

    def _glfw_callback_mouse_button(self, glfw_window, button, action, mods):
        for button in constants.MOUSE_BUTTONS:
            # NOTE: Button numbers already match the GLFW numbers in the constants
            if action == glfw.PRESS:
                self.mouse_state[button] = constants.BUTTON_PRESSED
            if action == glfw.RELEASE:
                self.mouse_state[button] = constants.BUTTON_RELEASED

    def _glfw_callback_mouse_move(self, glfw_window, x, y):
        self.mouse_state[constants.MOUSE_POSITION] = (x, y)
        self.imgui_renderer.mouse_callback(glfw_window, x, y)

    def _glfw_callback_mouse_scroll(self, glfw_window, x_offset, y_offset):
        self.mouse_state[constants.MOUSE_SCROLL_POSITION] += y_offset
        self.imgui_renderer.scroll_callback(glfw_window, x_offset, y_offset)

    def _glfw_callback_window_resize(self, glfw_window, width, height):
        self.window_size = (width, height)
        self.imgui_renderer.resize_callback(glfw_window, width, height)

    def _glfw_callback_framebuffer_size(self, glfw_window, width, height):
        pass
    
    def _glfw_callback_drop_files(self, glfw_window, file_list):
        pass

    # ========================================================================
    #                         Per Frame Update Functions
    # ========================================================================

    def _update_inputs(self):

        # Mouse Inputs
        for button in constants.MOUSE_BUTTONS:
            if self.mouse_state[button] == constants.BUTTON_PRESSED:
                self.mouse_state[button] = constants.BUTTON_DOWN

            if self.mouse_state[button] == constants.BUTTON_RELEASED:
                self.mouse_state[button] = constants.BUTTON_UP

        self.mouse_state[constants.MOUSE_POSITION_LAST_FRAME] = self.mouse_state[constants.MOUSE_POSITION]
        self.mouse_state[constants.MOUSE_SCROLL_POSITION_LAST_FRAME] = self.mouse_state[constants.MOUSE_SCROLL_POSITION]

    # ========================================================================
    #                      Application Callback Functions
    # ========================================================================

    def setup(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def shutdown(self):
        pass

    # ========================================================================
    #                             Main Function
    # ========================================================================

    def run(self):

        self.setup()

        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window_glfw)

        while not glfw.window_should_close(self.window_glfw):

            glfw.poll_events()
            self.imgui_renderer.process_inputs()

            self._update_inputs()

            imgui.new_frame()
            self.update()
            imgui.end()

            self.context.clear(0.0, 0.0, 0.0)

            # App Render
            self.render()

            imgui.render()
            self.imgui_renderer.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window_glfw)

        self.shutdown()

        self.imgui_renderer.shutdown()
        glfw.terminate()
