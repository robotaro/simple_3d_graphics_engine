from typing import List
import imgui

import moderngl_window as mglw
from moderngl_window import geometry
from moderngl_window.integrations.imgui import ModernglWindowRenderer

from src3 import constants
from src3.shader_loader import ShaderLoader
from src3.window_glfw import WindowGLFW
from src.utilities import utils_logging
from src3.event_publisher import EventPublisher

# Temporary
from src3.editors.viewer_3d import Viewer3D
from src3.editors.gltf_load_demo import GLTFLoadDemo


class AppMglWnd(mglw.WindowConfig):

    gl_version = (3, 3)
    title = "App"
    aspect_ratio = None

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.logger = utils_logging.get_project_logger(project_logger_name="Editor")
        self.shader_loader = ShaderLoader(logger=self.logger, ctx=self.ctx)
        self.event_publisher = EventPublisher(logger=self.logger)

        imgui.create_context()
        self.imgui_renderer = ModernglWindowRenderer(self.wnd)

        # Temporary
        self.editors = []

        self.shader_loader.load_shaders(directory=constants.SHADERS_DIR)

        editor_classes = [
            Viewer3D
        ]

        for editor_class in editor_classes:
            self.editors.append(editor_class(
                ctx=self.ctx,
                logger=self.logger,
                event_publisher=self.event_publisher,
                shader_loader=self.shader_loader,
                imgui_renderer=self.imgui_renderer,
                params={}
                )
            )

        # Initialise all editors and Subscribe them to all events
        for editor in self.editors:
            editor.setup()
            self.event_publisher.subscribe(listener=editor)

    def render(self, time: float, frametime: float):

        imgui.new_frame()
        for editor in self.editors:
            editor.update(time, elapsed_time=frametime)

        # DEBUG

        imgui.show_test_window()

        # Render UI to screen
        self.wnd.use()

        #imgui.end_frame()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def shutdown(self):
        for editor in self.editors:
            self.event_publisher.unsubscribe(listener=editor)
            editor.shutdown()

    def resize(self, width: int, height: int):
        self.imgui_renderer.resize(width, height)

    def files_dropped_event(self, x: int, y: int, paths: List[str]):
        pass

    def key_event(self, key, action, modifiers):
        self.imgui_renderer.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui_renderer.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui_renderer.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui_renderer.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui_renderer.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui_renderer.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui_renderer.unicode_char_entered(char)


if __name__ == '__main__':
    mglw.run_window_config(AppMglWnd)