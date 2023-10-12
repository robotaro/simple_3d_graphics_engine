import glfw
import moderngl
import imgui
import logging
from imgui.integrations.glfw import GlfwRenderer

from src import constants
from src.systems.system import System
from src.component_pool import ComponentPool
from src.event_publisher import EventPublisher
from src.action_publisher import ActionPublisher


class ImguiSystem(System):

    __slots__ = [
        "window_glfw",
        "imgui_renderer",
        "selected_entity_uid",
        "selected_entity_name",
        "selected_entity_components",
        "pass_window_hover",
        "_exit_popup_open"
    ]

    _type = "imgui_system"

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher,
                 parameters: dict,
                 **kwargs):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher,
                         parameters=parameters)

        self.window_glfw = kwargs["window_glfw"]
        self.imgui_renderer = None
        self.selected_entity_uid = -1
        self.selected_entity_name = ""
        self.selected_entity_components = []
        self.pass_window_hover = False

        # Flags
        self._exit_popup_open = False

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self) -> bool:

        # Step 1) Create ImGUI context first
        imgui.create_context()

        # Step 2) Only then create the GlfwRenderer. And don't make sure to disable attach_callbacks!
        self.imgui_renderer = GlfwRenderer(self.window_glfw, attach_callbacks=False)

        # TODO: Load custom fonts and set other global parameters once

        return True

    def update(self,
               elapsed_time: float,
               context: moderngl.Context) -> bool:

        self.imgui_renderer.process_inputs()
        imgui.get_io().ini_file_name = ""  # Disables creating an .ini file with the last window details
        imgui.new_frame()

        # Render menus and windows
        self.gui_main_menu_bar()
        self.gui_entity_window()

        if not self.gui_exit_modal():
            return False

        self.publish_events()

        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

        return True

    def on_event(self, event_type: int, event_data: tuple):

        # TODO: Find out whether I really need "on_event" callbacks if the
        #       "self.imgui_renderer.process_inputs()" gets all mouse and keyboard inputs

        if event_type == constants.EVENT_ENTITY_SELECTED and event_data[0] >= constants.COMPONENT_POOL_STARTING_ID_COUNTER:
            self.select_entity(entity_uid=event_data[0])

        if event_type == constants.EVENT_KEYBOARD_PRESS:
            if event_data[constants.EVENT_INDEX_KEYBOARD_KEY] == glfw.KEY_ESCAPE:
                self._exit_popup_open = True

    def shutdown(self):
        self.imgui_renderer.shutdown()

    # =========================================================================
    #                           Custom functions
    # =========================================================================

    def select_entity(self, entity_uid: int):
        self.selected_entity_uid = entity_uid
        entity = self.component_pool.entities.get(self.selected_entity_uid, None)
        if entity is not None:
            self.selected_entity_name = entity.name
        self.selected_entity_components = self.component_pool.get_all_components(entity_uid=entity_uid)
        self.event_publisher.publish(event_type=constants.EVENT_ENTITY_SELECTED,
                                     event_data=(entity_uid,),
                                     sender=self)

    def publish_events(self):
        # Enable/Disable mouse buttons to other systems if it is hovering on any Imgui windows
        windows_hover = imgui.is_window_hovered(imgui.HOVERED_ANY_WINDOW)

        if windows_hover and not self.pass_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_DISABLED,
                                         event_data=None,
                                         sender=self)

        if not windows_hover and self.pass_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_ENABLED,
                                         event_data=None,
                                         sender=self)
        self.pass_window_hover = windows_hover

    def gui_main_menu_bar(self):

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
                    self._exit_popup_open = True

                imgui.end_menu()

            # ========================[ Edit ]========================
            if imgui.begin_menu("Edit", True):
                if imgui.begin_menu("Light modes"):
                    _, default = imgui.menu_item("Default", None, True)

                    _, diffuse = imgui.menu_item("Diffuse", None, True)

                    imgui.end_menu()

                clicked, selected = imgui.menu_item("Preferences", "Ctrl + Q", False, True)

                imgui.end_menu()

    def gui_exit_modal(self):

        if self._exit_popup_open:
            imgui.open_popup("Exit##exit-popup")

        if imgui.begin_popup_modal("Exit##exit-popup", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)[0]:
            if self._exit_popup_open:
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
                    self._exit_popup_open = False

                imgui.pop_style_color()
                imgui.pop_style_color()
                imgui.pop_style_color()

                imgui.same_line()
                if imgui.button("exit", button_width):
                    return False
            else:
                imgui.close_current_popup()
            imgui.end_popup()

        return True

    def gui_entity_window(self):

        # open new window context
        imgui.begin(f"Selected Entity", True)

        imgui.set_window_size(500, 500)

        flags = imgui.SELECTABLE_ALLOW_ITEM_OVERLAP

        # ======================================================================
        #                 List all available entities in the scene
        # ======================================================================

        for entity_uid, entity in self.component_pool.entities.items():

            # Do not show any entities created and managed by the systems. They are required for them to work.
            if entity.system_owned:
                continue

            # Draw the selectable item
            (opened, selected) = imgui.selectable(entity.name, selected=False, flags=flags)

            if selected:
                self.select_entity(entity_uid=entity_uid)

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        # TODO: Think of a better way to go through components
        if len(self.selected_entity_components) == 0:
            imgui.end()
            return

        imgui.text(f"[ Entity ] {self.selected_entity_name}")
        imgui.spacing()

        # ======================================================================
        #            List all components of the currently selected entity
        # ======================================================================

        # [ Point Light ]
        point_light = self.component_pool.point_light_components.get(self.selected_entity_uid, None)
        if point_light and not point_light.system_owned:
            imgui.text(f"Colors")
            _, point_light.diffuse = imgui.drag_float3("Diffuse Color",
                                                       *point_light.diffuse,
                                                       0.005,
                                                       0.0,
                                                       1.0,
                                                       "%.3f")
            _, point_light.specular = imgui.drag_float3("Specular Color",
                                                        *point_light.specular,
                                                        0.005,
                                                        0.0,
                                                        1.0,
                                                        "%.3f")
            _, point_light.attenuation_coeffs = imgui.drag_float3("Attenuation Coeffs.",
                                                        *point_light.attenuation_coeffs,
                                                        0.005,
                                                        0.0,
                                                        100.0,
                                                        "%.3f")

            imgui.spacing()

        # [ Camera ]
        camera = self.component_pool.camera_components.get(self.selected_entity_uid, None)
        if camera and not camera.system_owned:
            imgui.text(f"Camera")
            _, camera.perspective = imgui.checkbox("Perspective", camera.perspective)

        # [ Transform 3D ]
        transform = self.component_pool.transform_3d_components.get(self.selected_entity_uid, None)
        if transform and not transform.system_owned:
            imgui.text(f"Transform")
            value_updated, transform.position = imgui.drag_float3("Position",
                                                                  *transform.position,
                                                                  constants.IMGUI_DRAG_FLOAT_PRECISION)
            transform.dirty |= value_updated
            value_updated, transform.rotation = imgui.drag_float3("Rotation",
                                                                  *transform.rotation,
                                                                  constants.IMGUI_DRAG_FLOAT_PRECISION)
            transform.dirty |= value_updated

            imgui.spacing()

        # [ Material]
        material = self.component_pool.material_components.get(self.selected_entity_uid, None)
        if material and not material.system_owned:
            imgui.text(f"Material")
            _, material.diffuse = imgui.color_edit3("Diffuse", *material.diffuse)
            _, material.specular = imgui.color_edit3("Specular", *material.specular)
            _, material.shininess_factor = imgui.drag_float("Shininess Factor",
                                                            material.shininess_factor,
                                                            0.05,
                                                            0.0,
                                                            32.0,
                                                            "%.3f")
            _, material.color_source = imgui.slider_int(
                "Color Source",
                material.color_source,
                min_value=constants.RENDER_MODE_COLOR_SOURCE_SINGLE,
                max_value=constants.RENDER_MODE_COLOR_SOURCE_UV)
            _, material.lighting_mode = imgui.slider_int(
                "Lighting Mode",
                material.lighting_mode,
                min_value=constants.RENDER_MODE_LIGHTING_SOLID,
                max_value=constants.RENDER_MODE_LIGHTING_LIT)

            imgui.spacing()

        # draw text label inside of current window
        imgui.end()
