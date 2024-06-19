import time
import glfw
import signal
import moderngl
import numpy as np
from abc import ABC, abstractmethod

# GUI
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src3 import constants
from src.utilities import utils_logging
from src3.event_publisher import EventPublisher


class WindowGLFW(ABC):

    """
    Main window class
    """

    __slots__ = ("logger",
                 "window_size",
                 "window_title",
                 "vertical_sync",
                 "mouse_state",
                 "keyboard_state",
                 "mouse_press_last_timestamp",
                 "window_glfw",
                 "monitor_gltf",
                 "ctx",
                 "buffer_size",
                 "event_publisher",
                 "close_application")

    def __init__(self,
                 window_size=constants.DEFAULT_EDITOR_WINDOW_SIZE,
                 window_title="New Editor",
                 vertical_sync=True):

        self.logger = utils_logging.get_project_logger()
        self.window_size = window_size
        self.buffer_size = window_size
        self.window_title = window_title
        self.vertical_sync = vertical_sync
        self.event_publisher = EventPublisher(logger=self.logger)

        # Input variables
        self.mouse_state = self.initialise_mouse_state()
        self.keyboard_state = self.initialise_keyboard_state()
        self.mouse_press_last_timestamp = time.perf_counter()

        if not glfw.init():
            raise ValueError("[ERROR] Failed to initialize GLFW")

        # TODO: Find out about samples hint before creating the window
        glfw.window_hint(glfw.SAMPLES, 4)

        self.monitor_gltf = glfw.get_primary_monitor()
        self.window_glfw = glfw.create_window(width=self.window_size[0],
                                              height=self.window_size[1],
                                              title=window_title,
                                              monitor=None,
                                              share=None)
        if not self.window_glfw:
            glfw.terminate()
            raise Exception('[ERROR] Could not create GLFW window.')

        # Set window to the center of the main monitor
        pos = glfw.get_monitor_pos(self.monitor_gltf)
        size = glfw.get_window_size(self.window_glfw)
        mode = glfw.get_video_mode(self.monitor_gltf)
        glfw.set_window_pos(
            self.window_glfw,
            int(pos[0] + (mode.size.width - size[0]) / 2),
            int(pos[1] + (mode.size.height - size[1]) / 2))

        glfw.make_context_current(self.window_glfw)
        glfw.swap_interval(1 if self.vertical_sync else 0)

        self.ctx = moderngl.create_context()

        # ImGUI
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window_glfw)  # DISABLE attach_callbacks!!!!
        self.imgui_exit_popup_open = False

        # Assign callback functions
        glfw.set_key_callback(self.window_glfw, self._glfw_callback_keyboard)
        glfw.set_char_callback(self.window_glfw, self._glfw_callback_char)
        glfw.set_cursor_pos_callback(self.window_glfw, self._glfw_callback_mouse_move)
        glfw.set_mouse_button_callback(self.window_glfw, self._glfw_callback_mouse_button)
        glfw.set_scroll_callback(self.window_glfw, self._glfw_callback_mouse_scroll)
        glfw.set_window_size_callback(self.window_glfw, self._glfw_callback_window_resize)
        glfw.set_framebuffer_size_callback(self.window_glfw, self._glfw_callback_framebuffer_size)
        glfw.set_drop_callback(self.window_glfw, self._glfw_callback_drop_files)

        # Update any initialisation variables after window GLFW has been created, if needed
        self.mouse_state[constants.MOUSE_POSITION] = glfw.get_cursor_pos(self.window_glfw)

        # Flags
        self.close_application = False

        # Add callbacks for application termination
        signal.signal(signal.SIGINT, self.callback_signal_handler)
        signal.signal(signal.SIGTERM, self.callback_signal_handler)

    def callback_signal_handler(self, signum, frame):
        self.logger.debug("Signal received : Closing editor now")
        self.close_application = True

    # ========================================================================
    #                           Input State Functions
    # ========================================================================

    @staticmethod
    def initialise_mouse_state() -> dict:
        return {
            constants.MOUSE_LEFT: constants.BUTTON_UP,
            constants.MOUSE_RIGHT: constants.BUTTON_UP,
            constants.MOUSE_MIDDLE: constants.BUTTON_UP,
            constants.MOUSE_POSITION: (0, 0),
            constants.MOUSE_POSITION_LAST_FRAME: (0, 0),
            constants.MOUSE_SCROLL_POSITION: 0
        }

    @staticmethod
    def initialise_keyboard_state() -> np.array:
        return np.ones((constants.KEYBOARD_SIZE,), dtype=np.int8) * constants.KEY_STATE_UP

    # ========================================================================
    #                       GLFW Callback functions
    # ========================================================================

    def _glfw_callback_char(self, glfw_window, char):
        pass

    def _glfw_callback_keyboard(self, glfw_window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_PRESS,
                                         event_data=(key, scancode, mods),
                                         sender=self)
            self.keyboard_state[key] = constants.KEY_STATE_DOWN

        if action == glfw.RELEASE:
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_RELEASE,
                                         event_data=(key, scancode, mods),
                                         sender=self)
            self.keyboard_state[key] = constants.KEY_STATE_UP

    def _glfw_callback_mouse_button(self, glfw_window, button, action, mods):

        mouse_position = (-1.0, -1.0)
        if glfw.get_window_attrib(self.window_glfw, glfw.FOCUSED):
            x, y_gui = glfw.get_cursor_pos(self.window_glfw)
            y_gl = self.window_size[1] - y_gui
            mouse_position = (x, y_gl, y_gui)

        # NOTE: Button numbers already match the GLFW numbers in the constants
        if action == glfw.PRESS:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_PRESS,
                                         event_data=(button, mods, *mouse_position),
                                         sender=self)
            self.mouse_state[button] = constants.BUTTON_PRESSED

            # Double click detection
            mouse_press_timestamp = time.perf_counter()
            time_between_clicks = mouse_press_timestamp - self.mouse_press_last_timestamp
            self.mouse_press_last_timestamp = mouse_press_timestamp
            if time_between_clicks < constants.DEFAULT_EDITOR_DOUBLE_CLICK_TIME_THRESHOLD:
                self.event_publisher.publish(event_type=constants.EVENT_MOUSE_DOUBLE_CLICK,
                                             event_data=(button, mods, *mouse_position),
                                             sender=self)

                # Three consecutive clicks may trigger two double clicks, so we reset the timestamp after a double click
                self.mouse_press_last_timestamp = 0

        if action == glfw.RELEASE:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_RELEASE,
                                         event_data=(button, mods, *mouse_position),
                                         sender=self)
            self.mouse_state[button] = constants.BUTTON_RELEASED

    def _glfw_callback_mouse_move(self, glfw_window, x, y):

        # We send both coordinate systems to help things out!
        y_gl = self.window_size[1] - y
        y_gui = y
        both_coordinates = (x, y_gl, y_gui)

        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_MOVE,
                                     event_data=both_coordinates,
                                     sender=self)

        self.mouse_state[constants.MOUSE_POSITION] = both_coordinates

    def _glfw_callback_mouse_scroll(self, glfw_window, x_offset, y_offset):
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_SCROLL,
                                     event_data=(x_offset, y_offset),
                                     sender=self)
        self.mouse_state[constants.MOUSE_SCROLL_POSITION] += y_offset

        # Since we overrode the glfw callbacks that imgui set, we need to provide the updates ourselves
        imgui.get_io().mouse_wheel_horizontal = x_offset
        imgui.get_io().mouse_wheel = y_offset

    def _glfw_callback_window_resize(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_SIZE,
                                     event_data=(width, height),
                                     sender=self)
        # TODO: Why doesn't window resize get called? Instead, only framebuffer is called
        self.window_size = (width, height)

    def _glfw_callback_framebuffer_size(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_FRAMEBUFFER_SIZE,
                                     event_data=(width, height),
                                     sender=self)

        # IMPORTANT: You need to update the final screen framebuffer viewport in order to render to the whole window!
        self.ctx.viewport = (0, 0, width, height)
        self.buffer_size = (width, height)

    def _glfw_callback_window_size(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_SIZE,
                                     event_data=(width, height),
                                     sender=self)
        self.window_size = (width, height)

    def _glfw_callback_drop_files(self, glfw_window, file_list):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_DROP_FILES,
                                     event_data=tuple(file_list),
                                     sender=self)

    def _update_inputs(self) -> None:

        """
        Internal function designed to update mouse button states
        :return:
        """

        # Mouse Inputs
        for button in constants.MOUSE_BUTTONS:
            if self.mouse_state[button] == constants.BUTTON_PRESSED:
                self.mouse_state[button] = constants.BUTTON_DOWN

            if self.mouse_state[button] == constants.BUTTON_RELEASED:
                self.mouse_state[button] = constants.BUTTON_UP

        self.mouse_state[constants.MOUSE_POSITION_LAST_FRAME] = self.mouse_state[constants.MOUSE_POSITION]
        self.mouse_state[constants.MOUSE_SCROLL_POSITION_LAST_FRAME] = self.mouse_state[
            constants.MOUSE_SCROLL_POSITION]

    def imgui_start(self):
        self.imgui_renderer.process_inputs()
        imgui.get_io().ini_file_name = ""  # Disables creating an .ini file with the last window details
        imgui.new_frame()

    def imgui_stop_and_render(self):

        imgui.end_frame()
        imgui.render()  # Doesn't really render, only sorts and organises the vertex data

        # Render all gui to screen
        self.ctx.screen.use()
        self.ctx.screen.clear()
        self.imgui_renderer.render(imgui.get_draw_data())

    @abstractmethod
    def initialise(self):
        self.logger.info("WindowGLFW initialised")

    @abstractmethod
    def update(self, elapsed_time: float):
        pass

    @abstractmethod
    def shutdown(self):
        self.logger.info("WindowGLFW shutdown")

    def run(self):
        """
        Main function to run the application. Currently, holds a few debugging variables but it will
        be cleaner in the future.

        :param profiling_enabled: bool,
        :param title_fps: bool, if TRUE, it wil change the title of the window for the average FPS
        :return:
        """

        self.initialise()

        # Prepare to enter main loop
        self.close_application = False
        timestamp_past = time.perf_counter()

        # Main loop
        while not glfw.window_should_close(self.window_glfw) and not self.close_application:

            # Update elapsed time
            timestamp = time.perf_counter()
            elapsed_time = timestamp - timestamp_past
            timestamp_past = timestamp

            # Process all OS events
            glfw.poll_events()

            # Render and Update goes here
            self.imgui_start()
            self.update(elapsed_time=elapsed_time)
            self.imgui_stop_and_render()

            # Still swap these even if you have to exit application?
            glfw.swap_buffers(self.window_glfw)

        self.shutdown()
