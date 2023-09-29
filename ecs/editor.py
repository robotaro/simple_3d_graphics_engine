import time
import glfw

import moderngl
import numpy as np
from typing import List, Union


# Systems
from ecs import constants
from ecs.systems.render_system.render_system import RenderSystem
from ecs.systems.imgui_system.imgui_system import ImguiSystem
from ecs.systems.input_control_system.input_control_system import InputControlSystem
from ecs.event_publisher import EventPublisher
from ecs.component_pool import ComponentPool
from ecs.utilities import utils_logging


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
                 "monitor_gltf",
                 "context",
                 "buffer_size",
                 "transform_components",
                 "camera_components",
                 "systems",
                 "component_pool",
                 "event_publisher")

    def __init__(self,
                 window_size=constants.DEFAULT_EDITOR_WINDOW_SIZE,
                 window_title="New Editor",
                 systems: Union[List[str], None] = None,
                 vertical_sync=True):

        self.logger = utils_logging.get_project_logger()
        self.window_size = window_size
        self.buffer_size = window_size
        self.window_title = window_title
        self.vertical_sync = vertical_sync

        # Core Variables
        self.systems = []
        self.component_pool = ComponentPool()
        self.event_publisher = EventPublisher()

        # Input variables
        self.mouse_state = self.initialise_mouse_state()
        self.keyboard_state = self.initialise_keyboard_state()

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

        # Set application icon - Disabled for now
        #icon_fpath = os.path.join(constants.IMAGES_DIR, "anime_eyes.png")
        #icon_image = Image.open(icon_fpath)
        #icon = Image.frombytes(icon_image.tobytes(), icon_image.size, icon_image.mode)
        #glfw.set_window_icon(self.window_glfw, 1, [icon_image])

        # Update any initialisation variables after window GLFW has been created, if needed
        self.mouse_state[constants.MOUSE_POSITION] = glfw.get_cursor_pos(self.window_glfw)

        # If not systems are specified, stick with the default ones
        if systems is None:
            systems = constants.DEFAULT_SYSTEMS_DECLARATION

        # Create systems
        for system_type in systems:
            self.create_system(system_type=system_type)

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

        mouse_pos = (-1, -1)
        if glfw.get_window_attrib(self.window_glfw, glfw.FOCUSED):
            mouse_pos = glfw.get_cursor_pos(self.window_glfw)
            mouse_pos = (int(mouse_pos[0]), self.window_size[1] - int(mouse_pos[1]))

        # NOTE: Button numbers already match the GLFW numbers in the constants
        if action == glfw.PRESS:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_PRESS,
                                         event_data=(button, mods, *mouse_pos),
                                         sender=self)
            self.mouse_state[button] = constants.BUTTON_PRESSED

        if action == glfw.RELEASE:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_RELEASE,
                                         event_data=(button, mods, *mouse_pos),
                                         sender=self)
            self.mouse_state[button] = constants.BUTTON_RELEASED

    def _glfw_callback_mouse_move(self, glfw_window, x, y):
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_MOVE,
                                     event_data=(x, y),
                                     sender=self)
        self.mouse_state[constants.MOUSE_POSITION] = (x, y)

    def _glfw_callback_mouse_scroll(self, glfw_window, x_offset, y_offset):
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_SCROLL,
                                     event_data=(x_offset, y_offset),
                                     sender=self)
        self.mouse_state[constants.MOUSE_SCROLL_POSITION] += y_offset

    def _glfw_callback_window_resize(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_SIZE,
                                     event_data=(width, height),
                                     sender=self)
        self.window_size = (width, height)

    def _glfw_callback_framebuffer_size(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_FRAMEBUFFER_SIZE,
                                     event_data=(width, height),
                                     sender=self)
        self.buffer_size = (width, height)

    def _glfw_callback_window_size(self, glfw_window, width, height):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_SIZE,
                                     event_data=(width, height),
                                     sender=self)
        self.buffer_size = (width, height)

    def _glfw_callback_drop_files(self, glfw_window, file_list):
        self.event_publisher.publish(event_type=constants.EVENT_WINDOW_DROP_FILES,
                                     event_data=tuple(file_list),
                                     sender=self)

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

    def create_system(self, system_type: str, subscribed_events: Union[List[int], None] = None) -> bool:

        new_system = None

        if system_type == RenderSystem._type:
            new_system = RenderSystem(
                logger=self.logger,
                component_pool=self.component_pool,
                event_publisher=self.event_publisher,
                context=self.context,
                buffer_size=self.buffer_size)

            # Set default events to subscribe too
            if subscribed_events is None:
                subscribed_events = constants.SUBSCRIBED_EVENTS_RENDER_SYSTEM

        if system_type == ImguiSystem._type:
            new_system = ImguiSystem(
                logger=self.logger,
                component_pool=self.component_pool,
                event_publisher=self.event_publisher,
                window_glfw=self.window_glfw)

            # Set default events to subscribe too
            if subscribed_events is None:
                subscribed_events = constants.SUBSCRIBED_EVENTS_IMGUI_SYSTEM

        if system_type == InputControlSystem._type:
            new_system = InputControlSystem(
                logger=self.logger,
                component_pool=self.component_pool,
                event_publisher=self.event_publisher
            )

            # Set default events to subscribe too
            if subscribed_events is None:
                subscribed_events = constants.SUBSCRIBED_EVENTS_INPUT_CONTROL_SYSTEM

        if new_system is None:
            self.logger.error(f"Failed to create system {system_type}")
            return False

        # Subscribe system to specific topics
        if subscribed_events is not None:
            for event_type in subscribed_events:
                self.event_publisher.subscribe(
                    event_type=event_type,
                    listener=new_system)

        # And finally add the new system to the roster
        self.systems.append(new_system)

    def load_scene(self, scene_xml_fpath: str):
        self.component_pool.load_scene(scene_xml_fpath=scene_xml_fpath)

    def initialise_components(self):

        # TODO: This is SORT OF a hack. Please think of a way to make this universal
        render_system = [system for system in self.systems if system._type == constants.SYSTEM_NAME_RENDER][0]

        for component_id, components in self.component_pool.component_storage_map.items():
            for entity_uid, component in components.items():
                component.initialise(ctx=self.context, shader_library=render_system.shader_program_library)

    def release_components(self):
        for component_id, components in self.component_pool.component_storage_map.items():
            for entity_uid, component in components.items():
                component.release()

    def run(self):

        # Initialise systems
        for system in self.systems:
            if not system.initialise():
                raise Exception(f"[ERROR] System {system._type} failed to initialise")

        self.initialise_components()

        # Update systems - Main Loop
        exit_application_now = False
        timestamp_past = time.perf_counter()
        while not glfw.window_should_close(self.window_glfw) and not exit_application_now:

            glfw.poll_events()

            # Measure time
            timestamp = time.perf_counter()
            elapsed_time = timestamp_past - timestamp
            timestamp_past = timestamp

            # Update All systems in order
            for system in self.systems:
                if not system.update(elapsed_time=elapsed_time,
                                     context=self.context):
                    exit_application_now = True
                    break

            # Still swap these even if you have to exit application?
            glfw.swap_buffers(self.window_glfw)

        # Shutdown systems
        for system in self.systems:
            system.shutdown()
