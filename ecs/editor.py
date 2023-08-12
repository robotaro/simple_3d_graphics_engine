import time
import timeit
import glfw
import moderngl
import numpy as np
from typing import List

from ecs import constants

from ecs.systems.system import System
from core.window import Window

from ecs.systems.system import System
from ecs.event_publisher import EventPublisher
from ecs.component_pool import ComponentPool

from core.utilities import utils_logging


class Editor:

    """
    Main Editor class that holds all the logic
    """

    __slots__ = ("logger",
                 "window_size",
                 "window_title",
                 "vertical_sync",
                 "mouse_state",
                 "keyboard_state",
                 "window_glfw",
                 "context",
                 "buffer_size",
                 "transform_components",
                 "camera_components",
                 "systems",
                 "component_pool",
                 "event_publisher")

    def __init__(self,
                 window_size=(1024, 768),
                 window_title="New Editor",
                 vertical_sync=False):

        self.logger = utils_logging.get_project_logger()
        self.window_size = window_size
        self.buffer_size = window_size
        self.window_title = window_title
        self.vertical_sync = vertical_sync

        # Core Variables
        self.systems = {}
        self.component_pool = ComponentPool()
        self.event_publisher = EventPublisher()

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
        pass

    def _glfw_callback_keyboard(self, glfw_window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_PRESS,
                                         event_data=(key, scancode, mods))
            self.keyboard_state[key] = constants.KEY_STATE_DOWN
        if action == glfw.RELEASE:
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_RELEASE,
                                         event_data=(key, scancode, mods))
            self.keyboard_state[key] = constants.KEY_STATE_UP

    def _glfw_callback_mouse_button(self, glfw_window, button, action, mods):

        # NOTE: Button numbers already match the GLFW numbers in the constants
        if action == glfw.PRESS:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_PRESS,
                                         event_data=(button, mods))
            self.mouse_state[button] = constants.BUTTON_PRESSED

        if action == glfw.RELEASE:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_RELEASE,
                                         event_data=(button, mods))
            self.mouse_state[button] = constants.BUTTON_RELEASED

    def _glfw_callback_mouse_move(self, glfw_window, x, y):
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_MOVE, event_data=(x, y))
        self.mouse_state[constants.MOUSE_POSITION] = (x, y)

    def _glfw_callback_mouse_scroll(self, glfw_window, x_offset, y_offset):
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_SCROLL, event_data=(x_offset, y_offset))
        self.mouse_state[constants.MOUSE_SCROLL_POSITION] += y_offset

    def _glfw_callback_window_resize(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_RESIZE, event_data=(width, height))
        self.window_size = (width, height)

    def _glfw_callback_framebuffer_size(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_FRAMEBUFFER_RESIZE,
                                     event_data=(width, height))
        self.buffer_size = (width, height)

    def _glfw_callback_drop_files(self, glfw_window, file_list):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_DROP_FILES,
                                     event_data=tuple(file_list))

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
        self.mouse_state[constants.MOUSE_SCROLL_POSITION_LAST_FRAME] = self.mouse_state[
            constants.MOUSE_SCROLL_POSITION]

    def from_yaml(self, yaml_fpath: str):
        """
        Loads the editor's systems and their respective parameters from the same
        :param yaml_fpath:
        :return:
        """
        pass

    def register_system(self, name: str, system: System, subscribed_events: List[int]):
        if name in self.systems:
            raise KeyError(f"[ERROR] System named 'name' already exists")

        # Add new system
        self.systems[name] = system

        # Subscribe system to specific topics
        for event_type in subscribed_events:
            self.event_publisher.subscribe(
                event_type=event_type,
                listener=system)

    def run(self):

        # Initialise systems
        for system_name, system in self.systems.items():
            if not system.initialise(
                logger=self.logger,
                context=self.context,
                window_glfw=self.window_glfw,
                buffer_size=self.buffer_size
            ):
                raise Exception(f"[ERROR] System {system_name} failed to initialise")

        # Update systems - Main Loop
        timestamp_past = time.perf_counter()
        while not glfw.window_should_close(self.window_glfw):

            glfw.poll_events()

            # Measure time
            timestamp = time.perf_counter()
            elapsed_time = timestamp_past - timestamp
            timestamp_past = timestamp

            # Update All systems
            for system_name, system in self.systems.items():
                system.update(elapsed_time=elapsed_time,
                              component_pool=self.component_pool,
                              context=self.context)

            glfw.swap_buffers(self.window_glfw)

            # DEBUG - Remove this!
            self.context.clear(
                red=0,
                green=0,
                blue=0,
                alpha=0.0,
                depth=1.0,
                viewport=self.buffer_size)

        # Shutdown systems
        for system_name, system in self.systems.items():
            system.shutdown()


if __name__ == "__main__":

    editor = Editor()
    editor.run()

