import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool


class ImguiSystem(System):

    _type = "imgui_system"

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"])
        self.window_glfw = kwargs["window_glfw"]
        self.imgui_renderer = None

    def initialise(self) -> bool:

        # Step 1) Create ImGUI context first
        imgui.create_context()

        # Step 2) Only then create the GlfwRenderer. And don't make sure to disable attach_callbacks!
        self.imgui_renderer = GlfwRenderer(self.window_glfw, attach_callbacks=False)

        return True

    def update(self,
               elapsed_time: float,
               component_pool: ComponentPool,
               context: moderngl.Context):

        self.imgui_renderer.process_inputs()
        imgui.new_frame()

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

        imgui.end()

        self.gui_main_menu_bar()

        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def on_event(self, event_type: int, event_data: tuple):
        # TODO: Find out whether I really need "on_event" callbacks if the "self.imgui_renderer.process_inputs()" gets all mouse and keyboard inputs
        if event_type == constants.EVENT_MOUSE_SCROLL:
            self.imgui_renderer.scroll_callback(None, event_data[0], event_data[1])

    def shutdown(self):
        self.imgui_renderer.shutdown()

    def gui_main_menu_bar(self):
        clicked_export = False
        clicked_screenshot = False

        with imgui.begin_main_menu_bar() as main_menu_bar:

            # ========================[ File ]========================
            if imgui.begin_menu("File", True):

                # File -> Load
                clicked, selected = imgui.menu_item("Load Scene", None, False, True)

                # File -> Save
                clicked, selected = imgui.menu_item("Save Scene", None, False, True)

                imgui.separator()

                # File -> Quit
                clicked, selected = imgui.menu_item("Quit", "Cmd+Q", False, True)
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
