
import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool


class ControllerSystem(System):

    def __init__(self):
        super().__init__()
        self.imgui_renderer = None
        self.window_glfw = None

    def initialise(self, **kwargs) -> bool:

        super().initialise(logger=kwargs["logger"])

        self.window_glfw = kwargs["window_glfw"]

        imgui.create_context()
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

        imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())


    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_MOUSE_SCROLL:
            self.imgui_renderer.scroll_callback(None, event_data[0], event_data[1])

    def shutdown(self):
        self.imgui_renderer.shutdown()
