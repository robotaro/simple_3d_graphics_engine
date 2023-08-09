import time
from typing import Dict, Type
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

from ecs.systems.system import System
from core.window import Window

from ecs.systems.system import System


class Editor(Window):

    """
    Main Editor class that holds all the logic
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Components
        self.transform_components = {}
        self.camera_components = {}
        self.vao_outline_pass_components = {}
        self.vao_forward_pass = {}

        # Systems
        #self.systems = Dict[str, Type[System]]
        self.systems = dict()

        pass

    def from_yaml(self, yaml_fpath: str):
        """
        Loads the editor's systems and their respective parameters from the same
        :param yaml_fpath:
        :return:
        """
        pass

    def register_system(self, name: str, system: System):
        if name in self.systems:
            raise KeyError(f"[ERROR] System named 'name' already exists")

        self.systems[name] = system

    def run(self):

        # Initialise systems
        for system_name, system in self.systems.items():
            if not system.initialize():
                raise Exception(f"[ERROR] System {system_name} failed to initialise")

        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window_glfw)

        # Main Loop
        timestamp_past = time.perf_counter()
        while not glfw.window_should_close(self.window_glfw):

            glfw.poll_events()
            self.imgui_renderer.process_inputs()

            imgui.new_frame()

            timestamp = time.perf_counter()
            elapsed_time = timestamp_past - timestamp
            for system_name, system in self.systems.items():
                system.update(elapsed_time=elapsed_time,
                              context=self.window_glfw.context,
                              event=None)
            timestamp_past = timestamp

            if self.imgui_enabled:
                imgui.render()
                self.imgui_renderer.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window_glfw)

        # Shutdown systems
        for system_name, system in self.systems.items():
            system.shutdown()


if __name__ == "__main__":

    editor = Editor(imgui_enabled=True)
    editor.run()

