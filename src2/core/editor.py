import os
import time
import glfw
import signal
import moderngl
import numpy as np

# Systems
from src.core import constants
from src.core import system_subscriptions
from src.systems.render_system.render_system import RenderSystem
from src.utilities import utils_io
from src.systems.imgui_system.imgui_system import ImguiSystem
from src.systems.gizmo_3d_system.gizmo_3d_system import Gizmo3DSystem
from src.systems.transform_system.transform_system import TransformSystem
from src.systems.input_control_system.input_control_system import InputControlSystem
from src.systems.import_system.import_system import ImportSystem
from src.systems.skeleton_system.skeleton_system import SkeletonSystem

from src.utilities import utils_logging
from src2.utilities import utils_scene_xml2json

# Core Modules
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src2.core.scene import Scene
from src.core.data_manager import DataManager


# Debug
import cProfile, pstats, io
from pstats import SortKey


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
                 "mouse_press_last_timestamp",
                 "window_glfw",
                 "monitor_gltf",
                 "ctx",
                 "buffer_size",
                 "scenes",
                 "event_publisher",
                 "action_publisher",
                 "data_manager",
                 "close_application",
                 "profiling_update_period",
                 "editor_num_updates",
                 "editor_sum_update_periods",
                 "events_average_period",
                 "events_num_updates",
                 "events_sum_update_periods",
                 "average_fps")

    def __init__(self,
                 window_size=constants.DEFAULT_EDITOR_WINDOW_SIZE,
                 window_title="New Editor",
                 system_names=constants.DEFAULT_SYSTEMS,
                 vertical_sync=True):

        self.logger = utils_logging.get_project_logger()
        self.window_size = window_size
        self.buffer_size = window_size
        self.window_title = window_title
        self.vertical_sync = vertical_sync

        # Core modules - MUST BE CREATED BEFORE ANY SYSTEM!
        self.scenes = {}
        self.event_publisher = EventPublisher(logger=self.logger)
        self.action_publisher = ActionPublisher(logger=self.logger)
        self.data_manager = DataManager(logger=self.logger)

        # Input variables
        self.mouse_state = self.initialise_mouse_state()
        self.keyboard_state = self.initialise_keyboard_state()
        self.mouse_press_last_timestamp = time.perf_counter()

        # Profiling variables
        self.editor_num_updates = 0
        self.editor_sum_update_periods = 0.0
        self.events_average_period = 0.0
        self.events_num_updates = 0
        self.events_sum_update_periods = 0.0
        self.profiling_update_period = constants.DEFAULT_EDITOR_PROFILING_UPDATE_PERIOD
        self.average_fps = 0.0  # Hz

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

        signal.signal(signal.SIGINT, self.callback_signal_handler)

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

    # ========================================================================
    #                         Per Frame Update Functions
    # ========================================================================

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

    def load_from_xml(self, xml_fpath: str):

        editor_setup = utils_scene_xml2json.editor_xml2json(xml_fpath=xml_fpath)

        # Step 1) Load resources
        for resource_id, resource_fpath in editor_setup[constants.EDITOR_BLUEPRINT_KEY_RESOURCES].items():
            self.data_manager.load_file(
                data_group_id=resource_id,
                fpath=utils_io.validate_resource_filepath(resource_fpath))

        # Step 3) Create scenes
        for scene_id, scene_dict in editor_setup[constants.EDITOR_BLUEPRINT_KEY_SCENES].items():
            new_scene = Scene(name=scene_id, logger=self.logger, ctx=self.ctx)

            # Shared components first
            for component_type, component_dict in scene_dict[constants.SCENE_BLUEPRINT_KEY_SHARED_COMPONENTS].items():
                for component_name, component_params in component_dict.items():
                    new_scene.create_shared_component(
                        shared_ref=component_name,
                        component_type=component_type,
                        params=component_params)

            # Then entities


            self.scenes[scene_id] = new_scene

    def release_components(self):
        for component_id, components in self.scene.component_storage_map.items():
            for entity_uid, component in components.items():
                component.release()

    def publish_startup_events(self):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_FRAMEBUFFER_SIZE,
                                     event_data=self.buffer_size,
                                     sender=self)

    def run(self):
        """
        Main function to run the application. Currently, holds a few debugging variables but it will
        be cleaner in the future.

        :param profiling_enabled: bool,
        :param title_fps: bool, if TRUE, it wil change the title of the window for the average FPS
        :return:
        """

        self.publish_startup_events()

        # Update systems - Main Loop
        self.close_application = False
        while not glfw.window_should_close(self.window_glfw) and not self.close_application:

            glfw.poll_events()

            # Update All systems in order
            for _, scene in self.scenes.items():
                scene.render()

            # Still swap these even if you have to exit application?
            glfw.swap_buffers(self.window_glfw)

        for _, scene in self.scenes.items():
            scene.destroy()

