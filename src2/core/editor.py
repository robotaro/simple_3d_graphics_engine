import time
import glfw
import signal
import moderngl
import numpy as np

# Systems
from src.core import constants
from src.utilities import utils_io
from src.utilities import utils_logging
from src2.utilities import utils_scene_xml2json

# Entities
from src2.entities.entity import Entity
from src2.entities.camera import Camera
from src2.entities.point_light import PointLight
from src2.entities.directional_light import DirectionalLight

# Components
from src2.components.transform import Transform
from src2.components.material import Material
from src2.components.mesh import Mesh

# Scenes
from src2.scenes.scene_3d import Scene3D
from src2.scenes.scene_2d import Scene2D

# Core Modules
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src2.scenes.scene import Scene
from src.core.data_manager import DataManager
from src2.core.shader_program_library import ShaderProgramLibrary


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
                 "entities",
                 "entity_groups",
                 "framebuffers",
                 "textures",
                 "ubos",
                 "components",
                 "event_publisher",
                 "action_publisher",
                 "data_manager",
                 "shader_library",
                 "registered_entity_types",
                 "registered_component_types",
                 "registered_scene_types",
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

        self.scenes = {}
        self.entities = {}
        self.components = {}
        self.entity_groups = {}
        self.ubos = {}

        self.registered_scene_types = {}
        self.registered_entity_types = {}
        self.registered_component_types = {}

        # Register entities
        self.register_entity_type(name="entity", entity_class=Entity)
        self.register_entity_type(name="camera", entity_class=Camera)
        self.register_entity_type(name="point_light", entity_class=PointLight)
        self.register_entity_type(name="directional_light", entity_class=DirectionalLight)

        # Register components
        self.register_component_type(name="mesh", component_clas=Mesh)
        self.register_component_type(name="transform", component_clas=Transform)
        self.register_component_type(name="material", component_clas=Material)

        # Register scenes
        self.register_scene_type(name="scene3d", scene_class=Scene3D)
        self.register_scene_type(name="scene2d", scene_class=Scene2D)

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

        # Create main moderngl Context
        self.ctx = moderngl.create_context()

        # Core modules
        self.event_publisher = EventPublisher(logger=self.logger)
        self.action_publisher = ActionPublisher(logger=self.logger)
        self.data_manager = DataManager(logger=self.logger)
        self.shader_library = ShaderProgramLibrary(logger=self.logger, ctx=self.ctx)

        # Initialise common graphics elements
        self.create_ubos()

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

    def register_scene_type(self, name: str, scene_class):
        if name in self.registered_scene_types:
            raise KeyError(f"[ERROR] Scene type {name} already registered")
        self.registered_scene_types[name] = scene_class

    def register_entity_type(self, name: str, entity_class):
        if name in self.registered_entity_types:
            raise KeyError(f"[ERROR] Entity type {name} already registered")
        self.registered_entity_types[name] = entity_class

    def register_component_type(self, name: str, component_clas):
        if name in self.registered_component_types:
            raise KeyError(f"[ERROR] Component type {name} already registered")
        self.registered_component_types[name] = component_clas

    def create_ubos(self):

        total_bytes = constants.SCENE_MATERIAL_STRUCT_SIZE_BYTES * constants.SCENE_MAX_NUM_MATERIALS
        self.ubos["materials"] = self.ctx.buffer(reserve=total_bytes)
        self.ubos["materials"].bind_to_uniform_block(binding=constants.UBO_BINDING_MATERIALS)

        total_bytes = constants.SCENE_POINT_LIGHT_STRUCT_SIZE_BYTES * constants.SCENE_MAX_NUM_POINT_LIGHTS
        zero_data = np.zeros(total_bytes, dtype='uint8')
        self.ubos["point_lights"] = self.ctx.buffer(data=zero_data.tobytes())
        self.ubos["point_lights"].bind_to_uniform_block(binding=constants.UBO_BINDING_POINT_LIGHTS)

        total_bytes = constants.SCENE_POINT_TRANSFORM_SIZE_BYTES * constants.SCENE_MAX_NUM_TRANSFORMS
        self.ubos["transforms"] = self.ctx.buffer(reserve=total_bytes)
        self.ubos["transforms"].bind_to_uniform_block(binding=constants.UBO_BINDING_TRANSFORMS)

    def callback_signal_handler(self, signum, frame):
        self.logger.debug("Signal received : Closing editor now")
        self.close_application = True

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
        for resource in editor_setup[constants.EDITOR_BLUEPRINT_KEY_RESOURCES]:
            self.data_manager.load_file(
                data_group_id=resource[constants.BLUEPRINT_KEY_ID],
                fpath=utils_io.validate_resource_filepath(resource[constants.BLUEPRINT_KEY_FPATH]))

        # Step 2) Create and initialise global components
        for component in editor_setup[constants.EDITOR_BLUEPRINT_KEY_COMPONENTS]:
            comp_id = component[constants.BLUEPRINT_KEY_ID]
            comp_type = component[constants.BLUEPRINT_KEY_TYPE]
            comp_params = component[constants.BLUEPRINT_KEY_PARAMS]

            if comp_id in self.components:
                raise KeyError(f"[ERROR] Global component ID '{comp_id}' already exists")

            component_class = self.registered_component_types.get(comp_type, None)
            self.components[comp_id] = component_class(
                params=comp_params,
                ctx=self.ctx,
                data_manager=self.data_manager,
                shader_library=self.shader_library)

        # Step 2) Load global entities
        for entity in editor_setup[constants.EDITOR_BLUEPRINT_KEY_ENTITIES]:
            entity_id = entity[constants.BLUEPRINT_KEY_ID]
            entity_type = entity[constants.BLUEPRINT_KEY_TYPE]
            entity_params = entity[constants.BLUEPRINT_KEY_PARAMS]

            if entity_id in self.entities:
                raise KeyError(f"[ERROR] Global entity ID '{entity_id}' already exists")

            entity_class = self.registered_entity_types.get(entity_type, None)
            if entity_class is None:
                raise KeyError(f"[ERROR] Entity type '{entity_type}' is not supported")
            self.entities[entity_id] = entity_class(params=entity_params)

            # And hand its internal components
            for comp_type, component in entity[constants.BLUEPRINT_KEY_COMPONENTS].items():

                # If this component points to a global component, then just fetch it
                ref_id = component.get(constants.BLUEPRINT_KEY_REF_ID, None)
                if ref_id:
                    self.entities[entity_id].components[comp_type] = self.components[ref_id]
                    continue

                comp_params = component[constants.BLUEPRINT_KEY_PARAMS]
                component_class = self.registered_component_types.get(comp_type, None)
                self.entities[entity_id].components[comp_type] = component_class(
                    params=comp_params,
                    ctx=self.ctx,
                    data_manager=self.data_manager,
                    shader_library=self.shader_library)

        # Step 3) Load Scenes
        for scene in editor_setup[constants.EDITOR_BLUEPRINT_KEY_SCENES]:

            scene_id = scene[constants.BLUEPRINT_KEY_ID]
            scene_type = scene[constants.BLUEPRINT_KEY_TYPE]

            scene_class = self.registered_scene_types.get(scene_type, None)
            if scene_class is None:
                raise KeyError(f"[ERROR] Scene type '{scene_type}' is not registered")

            if scene_id in self.scenes:
                raise KeyError(f"[ERROR] Scene ID '{scene_id}' already exists")

            new_scene = scene_class(params=scene[constants.BLUEPRINT_KEY_PARAMS],
                                    logger=self.logger,
                                    ctx=self.ctx,
                                    ubos=self.ubos,
                                    initial_window_size=self.window_size,
                                    shader_library=self.shader_library)

            for entity in scene[constants.EDITOR_BLUEPRINT_KEY_ENTITIES]:

                # TODO: Only referenced global entities are supported
                entity_ref_id = entity[constants.BLUEPRINT_KEY_REF_ID]

                if entity_ref_id not in self.entities:
                    raise KeyError(f"[ERROR] Scene entity ref_id '{entity_ref_id}' not declared in global entities")

                new_scene.attach_entity(entity_id=entity_ref_id,
                                        entity=self.entities[entity_ref_id])

            self.scenes[scene_id] = new_scene

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

            for _, scene in self.scenes.items():
                scene.render()

            # Still swap these even if you have to exit application?
            glfw.swap_buffers(self.window_glfw)

        for _, scene in self.scenes.items():
            scene.destroy()

    def shutdown(self):

        for _, scene in self.scenes.items():

            # Release all entities
            for component_id, component in scene.shared_components.items():
                component.release()

            # Release all shared components
            for component_id, component in scene.shared_components.items():
                component.release()

        for _, scene in self.scenes.items():
            scene.destroy()
