import glfw
import moderngl
import imgui
import json
from imgui.integrations.glfw import GlfwRenderer

from src.core import constants
from src.systems.system import System
from src.core.scene import ComponentPool
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher


class ImguiSystem(System):

    __slots__ = [
        "window_glfw",
        "imgui_renderer",
        "selected_entity_uid",
        "selected_entity_name",
        "selected_entity_components",
        "selected_resource_uid",
        "selected_resource",
        "past_window_hover",
        "_exit_popup_open",
        "system_profiling_event_data",
        "gizmo_mode"]

    name = constants.SYSTEM_NAME_IMGUI

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.window_glfw = kwargs["window_glfw"]
        self.imgui_renderer = None
        self.selected_entity_uid = -1
        self.selected_entity_name = ""
        self.selected_entity_components = []
        self.selected_resource_uid = -1
        self.selected_resource = None

        self.past_window_hover = False

        # Profiling
        self.system_profiling_event_data = ()

        # Register Event handlers
        self.event_handlers[constants.EVENT_ENTITY_SELECTED] = self.handle_event_entity_selected
        self.event_handlers[constants.EVENT_KEYBOARD_PRESS] = self.handle_event_keyboard_press
        self.event_handlers[constants.EVENT_PROFILING_SYSTEM_PERIODS] = self.handle_event_profiling_system_periods

        # Flags
        self._exit_popup_open = False

        # Temporary variables that will be removed on the next major refactoring
        self.gizmo_mode = constants.GIZMO_3D_ORIENTATION_GLOBAL

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
        self.gui_main_window()

        if not self.gui_exit_modal():
            return False

        self.publish_events()

        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

        return True

    def shutdown(self):
        self.imgui_renderer.shutdown()

    # =========================================================================
    #                           Event Handlers
    # =========================================================================

    def handle_event_entity_selected(self, event_data: tuple):
        if event_data[0] < constants.COMPONENT_POOL_STARTING_ID_COUNTER:
            return
        self.select_entity(entity_uid=event_data[0])

    def handle_event_keyboard_press(self, event_data: tuple):
        if event_data[constants.EVENT_INDEX_KEYBOARD_KEY] == glfw.KEY_ESCAPE:
            self._exit_popup_open = True

    def handle_event_profiling_system_periods(self, event_data: tuple):
        self.system_profiling_event_data = event_data

    # =========================================================================
    #                           Custom functions
    # =========================================================================

    def select_entity(self, entity_uid: int):
        self.selected_entity_uid = entity_uid
        entity = self.component_pool.entities.get(self.selected_entity_uid, None)
        if entity is not None:
            self.selected_entity_name = entity.name
        self.selected_entity_components = self.component_pool.get_all_components(entity_uid=entity_uid)

    def publish_events(self):
        # Enable/Disable mouse buttons to other systems if it is hovering on any Imgui windows
        windows_hover = imgui.is_window_hovered(imgui.HOVERED_ANY_WINDOW)

        if windows_hover and not self.past_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_ENTER_UI,
                                         event_data=(),
                                         sender=self)

        if not windows_hover and self.past_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_LEAVE_UI,
                                         event_data=(),
                                         sender=self)
        self.past_window_hover = windows_hover

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

    def gui_main_window(self):

        # open new window context
        imgui.begin(f"Inspection Window", True)

        with imgui.begin_tab_bar("MyTabBar") as tab_bar:
            if tab_bar.opened:
                with imgui.begin_tab_item("Entities") as item1:
                    if item1.selected:
                        self.gui_tab_entities()

                with imgui.begin_tab_item("Profiling") as item2:
                    if item2.selected:
                        self.gui_tab_profiling()

                with imgui.begin_tab_item("Gizmo 3D") as item3:
                    if item3.selected:
                        self.gui_tab_gizmo_3d()

                with imgui.begin_tab_item("Resources") as item4:
                    if item4.selected:
                        self.gui_tab_resources()

        # imgui.set_window_position(300, 150)
        imgui.set_window_size(500, 500)

        # ======================================================================
        #                 List all available entities in the scene
        # ======================================================================

        # draw text label inside of current window
        imgui.end()

    def gui_tab_profiling(self):
        for i in range(len(self.system_profiling_event_data) // 2):
            name = self.system_profiling_event_data[i * 2]
            period = self.system_profiling_event_data[i * 2 + 1]
            imgui.text(f"{name} : {period * 1000.0:.3f} ms")

    def gui_tab_gizmo_3d(self):

        imgui.text(f"Gizmo 3D")
        updated, self.gizmo_mode = imgui.slider_int(
            "Orientation",
            self.gizmo_mode,
            min_value=constants.GIZMO_3D_ORIENTATION_GLOBAL,
            max_value=constants.GIZMO_3D_ORIENTATION_LOCAL)

        if updated:
            self.event_publisher.publish(event_type=constants.EVENT_GIZMO_3D_SYSTEM_PARAMETER_UPDATED,
                                         event_data=("orientation", self.gizmo_mode),
                                         sender=self)

    def gui_tab_entities(self):

        flags = imgui.SELECTABLE_ALLOW_ITEM_OVERLAP

        imgui.text(f"[ All Scene Entities ]")
        imgui.spacing()

        for entity_uid, entity in self.component_pool.entities.items():

            # Do not show any entities created and managed by the systems. They are required for them to work.
            if entity.system_owned:
                continue

            # Draw the selectable item
            (opened, selected) = imgui.selectable(entity.name, selected=False, flags=flags)

            if selected:
                # Here the entity selection is initiated from the GUI, so you publish the respective event now.
                self.select_entity(entity_uid=entity_uid)
                self.event_publisher.publish(event_type=constants.EVENT_ENTITY_SELECTED,
                                             event_data=(entity_uid,),
                                             sender=self)

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        if len(self.selected_entity_components) == 0:
            return

        imgui.text(f"[ Selected Entity ] {self.selected_entity_name}")
        imgui.spacing()

        # ======================================================================
        #            List all components of the currently selected entity
        # ======================================================================

        # [ Point Light ]
        point_light_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_POINT_LIGHT)
        point_light = point_light_pool.get(self.selected_entity_uid, None)
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
        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        camera = camera_pool.get(self.selected_entity_uid, None)
        if camera and not camera.system_owned:
            imgui.text(f"Camera")
            _, camera.is_perspective = imgui.checkbox("Perspective", camera.is_perspective)

        # [ Transform 3D ]
        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
        transform = transform_3d_pool.get(self.selected_entity_uid, None)
        if transform and not transform.system_owned:
            imgui.text(f"Transform")
            value_updated, transform.position = imgui.drag_float3("Position",
                                                                  *transform.position,
                                                                  constants.IMGUI_DRAG_FLOAT_PRECISION)
            transform.input_values_updated |= value_updated
            value_updated, transform.rotation = imgui.drag_float3("Rotation",
                                                                  *transform.rotation,
                                                                  constants.IMGUI_DRAG_FLOAT_PRECISION)
            transform.input_values_updated |= value_updated
            value_updated, transform.scale = imgui.drag_float3("Scale",
                                                               *transform.scale,
                                                               constants.IMGUI_DRAG_FLOAT_PRECISION)
            transform.input_values_updated |= value_updated

            imgui.spacing()

        # [ Material]
        material_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)
        material = material_pool.get(self.selected_entity_uid, None)
        if material and not material.system_owned:
            imgui.text(f"Material")
            _, material.diffuse = imgui.color_edit3("Diffuse", *material.diffuse)
            _, material.diffuse_highlight = imgui.color_edit3("Diffuse Highlight", *material.diffuse_highlight)
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

    def gui_tab_resources(self):

        resource_ids = list(self.data_manager.data_groups.keys())
        resource_ids.sort()

        flags = imgui.SELECTABLE_ALLOW_ITEM_OVERLAP

        imgui.spacing()

        for resource_id in resource_ids:

            # Draw the selectable item
            (opened, selected) = imgui.selectable(resource_id, selected=False, flags=flags)

            if selected:
                # Here the entity selection is initiated from the GUI, so you publish the respective event now.
                self.selected_resource_uid = resource_id
                self.selected_resource = self.data_manager.data_groups[resource_id]

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        if self.selected_resource is None:
            return

        imgui.text(f"[ Resource ] '{self.selected_resource_uid}'")
        imgui.spacing()

        for data_blocks_name, data_block in self.selected_resource.data_blocks.items():

            imgui.text(f"DataBlock : '{data_blocks_name}' ")
            imgui.text(f" - DataShape: {data_block.data.shape}")
            imgui.text(f" - DataType: {data_block.data.dtype}")
            imgui.text(f" - Metadata: {json.dumps(data_block.metadata, indent=2)}")
            imgui.spacing()



