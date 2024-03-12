import copy
import time
import glfw
import yaml
import signal
import moderngl
import numpy as np
import logging

# GUI
import imgui
from imgui.integrations.glfw import GlfwRenderer

# Systems
from src2.core import constants
from src.utilities import utils_io
from src.utilities import utils_logging
from src2.utilities import utils_params
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

# Render Stages
from src2.render_stages.render_stage_forward import RenderStageForward
from src2.render_stages.render_stage_selection import RenderStageSelection
from src2.render_stages.render_stage_overlay import RenderStageOverlay
from src2.render_stages.render_stage_shadow import RenderStageShadow
from src2.render_stages.render_stage_screen import RenderStageScreen

# Scenes
from src2.scenes.scene_3d import Scene3D
from src2.scenes.scene_2d import Scene2D

# Modules
from src2.modules.scene_editor import SceneEditor

# Core components
from src2.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src2.scenes.scene import Scene
from src.core.data_manager import DataManager
from src2.core.shader_program_library import ShaderProgramLibrary


class Engine:

    """
    Main Engine class that holds does all the rendering and a few other tasks regarding window and input management
    """

    __slots__ = ("config",
                 "main_settings",
                 "logger",
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
                 "modules",
                 "components",
                 "imgui_renderer",
                 "event_publisher",
                 "action_publisher",
                 "data_manager",
                 "shader_library",
                 "registered_entities",
                 "registered_components",
                 "registered_scenes",
                 "registered_modules",
                 "close_application",
                 "imgui_exit_popup_open")

    def __init__(self, config_fpath=constants.APP_CONFIG_FPATH, log_level="warning"):

        self.config = {}
        with open(config_fpath, 'r') as file:
            self.config = yaml.safe_load(file)

        self.main_settings = self.config.get("main_settings", {})
        self.logger = utils_logging.get_project_logger()
        self.logger.setLevel(level=constants.LOGGING_MAP[log_level])
        self.window_size = utils_params.list2tuple(
            self.main_settings.get("window_size",
            constants.DEFAULT_EDITOR_WINDOW_SIZE))
        self.buffer_size = copy.copy(self.window_size)
        self.window_title = self.main_settings.get("window_title", "Editor")
        self.vertical_sync = self.main_settings.get("vertical_sync", False)

        self.scenes = {}
        self.entities = {}
        self.components = {}
        self.entity_groups = {}
        self.ubos = {}

        self.registered_scenes = {}
        self.registered_entities = {}
        self.registered_components = {}
        self.registered_modules = {}

        # Register components
        self.register_component(name="mesh", component_class=Mesh)
        self.register_component(name="transform", component_class=Transform)
        self.register_component(name="material", component_class=Material)

        # Register entities
        self.register_entity(name="entity", entity_class=Entity)
        self.register_entity(name="camera", entity_class=Camera)
        self.register_entity(name="point_light", entity_class=PointLight)
        self.register_entity(name="directional_light", entity_class=DirectionalLight)

        # Register scenes
        self.register_scene(name="scene3d", scene_class=Scene3D)
        self.register_scene(name="scene2d", scene_class=Scene2D)

        # Register Render passes
        self.register_render_stage(name="forward", render_stage_class=RenderStageForward)
        self.register_render_stage(name="selection", render_stage_class=RenderStageSelection)
        self.register_render_stage(name="overlay", render_stage_class=RenderStageOverlay)
        self.register_render_stage(name="shadow", render_stage_class=RenderStageShadow)
        self.register_render_stage(name="screen", render_stage_class=RenderStageScreen)

        # Register Modules
        self.register_module(name="scene_editor", module_class=SceneEditor)

        # Input variables
        self.mouse_state = self.initialise_mouse_state()
        self.keyboard_state = self.initialise_keyboard_state()
        self.mouse_press_last_timestamp = time.perf_counter()

        if not glfw.init():
            raise ValueError("[ERROR] Failed to initialize GLFW")

        # Create GLFW window
        self.monitor_gltf = glfw.get_primary_monitor()
        self.window_glfw = glfw.create_window(width=self.window_size[0],
                                              height=self.window_size[1],
                                              title=self.window_title,
                                              monitor=None,
                                              share=None)
        if not self.window_glfw:
            glfw.terminate()
            raise Exception('[ERROR] Could not create GLFW window.')

        # Set window to the center of the main monitor
        self.center_window_to_main_monitor()

        # Finish initialising GLFW context
        glfw.window_hint(glfw.SAMPLES, 4)  # TODO: Find out about samples hint before creating the window
        glfw.make_context_current(self.window_glfw)
        glfw.swap_interval(1 if self.vertical_sync else 0)

        # Assign callback functions
        glfw.set_key_callback(self.window_glfw, self._glfw_callback_keyboard)
        glfw.set_char_callback(self.window_glfw, self._glfw_callback_char)
        glfw.set_cursor_pos_callback(self.window_glfw, self._glfw_callback_mouse_move)
        glfw.set_mouse_button_callback(self.window_glfw, self._glfw_callback_mouse_button)
        glfw.set_scroll_callback(self.window_glfw, self._glfw_callback_mouse_scroll)
        glfw.set_window_size_callback(self.window_glfw, self._glfw_callback_window_resize)
        glfw.set_framebuffer_size_callback(self.window_glfw, self._glfw_callback_framebuffer_size)
        glfw.set_drop_callback(self.window_glfw, self._glfw_callback_drop_files)

        # Create main moderngl Context
        self.ctx = moderngl.create_context()

        # Core modules
        self.event_publisher = EventPublisher(logger=self.logger)
        self.action_publisher = ActionPublisher(logger=self.logger)
        self.data_manager = DataManager(logger=self.logger)
        self.shader_library = ShaderProgramLibrary(
            logger=self.logger,
            shader_program_definitions=self.config.get("shader_programs", {}),
            ctx=self.ctx)

        # General Modules
        self.modules = []
        self.create_modules(module_definitions=self.config.get("modules", {}))

        # ImGUI
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window_glfw, attach_callbacks=False)  # DISABLE attach_callbacks!!!!
        self.imgui_exit_popup_open = False

        # Initialise common graphics elements
        self.create_ubos()

        # Update any initialisation variables after window GLFW has been created, if needed
        self.mouse_state[constants.MOUSE_POSITION] = glfw.get_cursor_pos(self.window_glfw)

        # Flags
        self.close_application = False

        # Assign OS signal handling callback
        signal.signal(signal.SIGINT, self.callback_signal_handler)

    def register_scene(self, name: str, scene_class):
        if name in self.registered_scenes:
            raise KeyError(f"[ERROR] Scene type {name} already registered")
        self.registered_scenes[name] = scene_class

    def register_entity(self, name: str, entity_class):
        if name in self.registered_entities:
            raise KeyError(f"[ERROR] Entity type {name} already registered")
        self.registered_entities[name] = entity_class

    def register_component(self, name: str, component_class):
        if name in self.registered_components:
            raise KeyError(f"[ERROR] Component type {name} already registered")
        self.registered_components[name] = component_class

    def register_render_stage(self, name: str, render_stage_class):
        pass

    def register_module(self, name: str, module_class):
        if name in self.registered_modules:
            raise KeyError(f"[ERROR] Module type {name} already registered")
        self.registered_modules[name] = module_class

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

    def create_modules(self, module_definitions: dict):

        for module_name, all_params in module_definitions.items():

            subscribed_events = all_params.get("subscribed_events", {})
            params = {key: value for key, value in all_params.items() if key != "subscribed_events"}

            # Create new module
            new_module = self.registered_modules[module_name](
                logger=self.logger,
                event_publisher=self.event_publisher,
                action_publisher=self.action_publisher,
                data_manager=self.data_manager,
                params=params)
            self.logger.debug(f"Module Created: {module_name}")

            # Make it a listener to all events it subscribes to
            for event_name in subscribed_events:
                self.event_publisher.subscribe(event_type=event_name, listener=new_module)
                self.logger.debug(f"Module '{module_name}' subscribed to event: {event_name}")

            self.modules.append(new_module)

    def center_window_to_main_monitor(self):
        pos = glfw.get_monitor_pos(self.monitor_gltf)
        size = glfw.get_window_size(self.window_glfw)
        mode = glfw.get_video_mode(self.monitor_gltf)
        glfw.set_window_pos(
            self.window_glfw,
            int(pos[0] + (mode.size.width - size[0]) / 2),
            int(pos[1] + (mode.size.height - size[1]) / 2))

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

            component_class = self.registered_components.get(comp_type, None)
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

            entity_class = self.registered_entities.get(entity_type, None)
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
                component_class = self.registered_components.get(comp_type, None)
                self.entities[entity_id].components[comp_type] = component_class(
                    params=comp_params,
                    ctx=self.ctx,
                    data_manager=self.data_manager,
                    shader_library=self.shader_library)

        # Step 3) Load Scenes
        for scene in editor_setup[constants.EDITOR_BLUEPRINT_KEY_SCENES]:

            scene_id = scene[constants.BLUEPRINT_KEY_ID]
            scene_type = scene[constants.BLUEPRINT_KEY_TYPE]

            scene_class = self.registered_scenes.get(scene_type, None)
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

    def create_scene(self, name: str):
        pass

    def run(self):
        """
        Main function to run the application. Currently, holds a few debugging variables but it will
        be cleaner in the future.

        :param profiling_enabled: bool,
        :param title_fps: bool, if TRUE, it wil change the title of the window for the average FPS
        :return:
        """

        self.publish_startup_events()

        # Main loop
        self.close_application = False
        previous_time = time.perf_counter()
        while not glfw.window_should_close(self.window_glfw) and not self.close_application:

            # Clear the screen to black
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)

            glfw.poll_events()

            current_time = time.perf_counter()
            elapsed_time = current_time - previous_time
            previous_time = current_time

            self.imgui_start()

            for module in self.modules:
                if not module.enabled:
                    continue
                module.update(elapsed_time=elapsed_time)

            self.imgui_main_menu_bar()
            self.imgui_exit_modal()
            self.imgui_stop()

            glfw.swap_buffers(self.window_glfw)

        for _, scene in self.scenes.items():
            scene.destroy()

    def imgui_start(self):
        self.imgui_renderer.process_inputs()
        imgui.get_io().ini_file_name = ""  # Disables creating an .ini file with the last window details
        imgui.new_frame()

    def imgui_stop(self):
        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def imgui_main_menu_bar(self):

        with imgui.begin_main_menu_bar() as main_menu_bar:

            # ========================[ File ]========================
            if imgui.begin_menu("File", True):

                # File -> Load
                clicked, selected = imgui.menu_item("Load Scene", None, False, True)

                # File -> Save
                clicked, selected = imgui.menu_item("Save Scene", None, False, True)

                imgui.separator()

                # File -> Quit
                clicked, selected = imgui.menu_item("Quit", "Ctrl + Q", False, True)
                if clicked:
                    self.imgui_exit_popup_open = True

                imgui.end_menu()

            # ========================[ Edit ]========================
            if imgui.begin_menu("Edit", True):
                if imgui.begin_menu("Light modes"):
                    _, default = imgui.menu_item("Default", None, True)

                    _, diffuse = imgui.menu_item("Diffuse", None, True)

                    imgui.end_menu()

                clicked, selected = imgui.menu_item("Preferences", "Ctrl + Q", False, True)

                imgui.end_menu()

            # ========================[ Modules ]========================
            if imgui.begin_menu("Modules", True):
                for module in self.modules:
                    _, module.enabled = imgui.menu_item(module.label, None, module.enabled, True)
                imgui.end_menu()

    def imgui_exit_modal(self):

        if not self.imgui_exit_popup_open:
            return

        imgui.open_popup("Exit##exit-popup")

        if not imgui.begin_popup_modal("Exit##exit-popup", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)[0]:
            return

        imgui.text("Are you sure you want to exit?")
        imgui.spacing()

        # Draw a cancel and exit button on the same line using the available space
        button_width = (imgui.get_content_region_available()[0] - imgui.get_style().item_spacing[0]) * 0.5

        # Style the cancel with a grey color
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.5, 0.5, 0.5, 1.0)
        imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.6, 0.6, 0.6, 1.0)
        imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.7, 0.7, 0.7, 1.0)

        if imgui.button("cancel", width=button_width):
            imgui.close_current_popup()
            self.imgui_exit_popup_open = False

        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_color()

        imgui.same_line()
        if imgui.button("exit", button_width):
            self.close_application = True

        imgui.end_popup()

    def shutdown(self):

        for module in self.modules:
            module.shutdown()

        for _, scene in self.scenes.items():

            # Release all entities
            for component_id, component in scene.shared_components.items():
                component.release()

            # Release all shared components
            for component_id, component in scene.shared_components.items():
                component.release()

        for _, scene in self.scenes.items():
            scene.destroy()
