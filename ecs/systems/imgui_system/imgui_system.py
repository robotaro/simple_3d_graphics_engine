import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool


class ImguiSystem(System):

    __slots__ = [
        "window_glfw",
        "imgui_renderer",
        "selected_entity_uid",
        "selected_entity_name",
        "selected_entity_components",
        "pass_window_hover"
    ]

    _type = "imgui_system"

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"],
                         component_pool=kwargs["component_pool"],
                         event_publisher=kwargs["event_publisher"])

        self.window_glfw = kwargs["window_glfw"]
        self.imgui_renderer = None
        self.selected_entity_uid = -1
        self.selected_entity_name = ""
        self.selected_entity_components = []
        self.pass_window_hover = False

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self) -> bool:

        # Step 1) Create ImGUI context first
        imgui.create_context()

        # Step 2) Only then create the GlfwRenderer. And don't make sure to disable attach_callbacks!
        self.imgui_renderer = GlfwRenderer(self.window_glfw, attach_callbacks=False)

        return True

    def update(self,
               elapsed_time: float,
               context: moderngl.Context):

        self.imgui_renderer.process_inputs()
        imgui.get_io().ini_file_name = ""  # Disables creating an .ini file with the last window details
        imgui.new_frame()

        self.gui_main_menu_bar()

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

        imgui.end()

        self.gui_entity_window()

        self.publish_events()

        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def on_event(self, event_type: int, event_data: tuple):

        # TODO: Find out whether I really need "on_event" callbacks if the
        #       "self.imgui_renderer.process_inputs()" gets all mouse and keyboard inputs

        # Component has been selected
        self.selected_entity_components = []
        if event_type == constants.EVENT_ACTION_ENTITY_SELECTED and event_data[0] >= constants.COMPONENT_POOL_STARTING_ID_COUNTER:
            self.selected_entity_uid = event_data[0]
            entity = self.component_pool.entities.get(self.selected_entity_uid, None)
            if entity is not None:
                self.selected_entity_name = entity.name
            self.selected_entity_components = self.component_pool.get_all_components(entity_uid=event_data[0])

    def shutdown(self):
        self.imgui_renderer.shutdown()

    # =========================================================================
    #                           Custom functions
    # =========================================================================

    def publish_events(self):
        # Enable/Disable mouse buttons to other systems if it is hovering on any Imgui windows
        windows_hover = imgui.is_window_hovered(imgui.HOVERED_ANY_WINDOW)
        if windows_hover and not self.pass_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_DISABLED, event_data=None)
        if not windows_hover and self.pass_window_hover:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_ENABLED, event_data=None)
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
                    exit(1)

                imgui.end_menu()

            # ========================[ Edit ]========================
            if imgui.begin_menu("Edit", True):
                if imgui.begin_menu("Light modes"):
                    _, default = imgui.menu_item("Default", None, True)

                    _, diffuse = imgui.menu_item("Diffuse", None, True)

                    imgui.end_menu()

                clicked, selected = imgui.menu_item("Preferences", "Ctrl + Q", False, True)

                imgui.end_menu()

    def gui_entity_window(self):

        # TODO: Think of a better way to go through components
        if len(self.selected_entity_components) == 0:
            return

        # open new window context
        imgui.begin(f"Selected Entity", True)

        transform = self.component_pool.transform_3d_components.get(self.selected_entity_uid, None)
        if transform:
            _, transform.position = imgui.drag_float3("Position",
                                                      *transform.position,
                                                      constants.IMGUI_DRAG_FLOAT_PRECISION)

        # draw text label inside of current window
        imgui.text(f"Entity: {self.selected_entity_name}")

        imgui.end()
