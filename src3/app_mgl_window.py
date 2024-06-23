from typing import List
import imgui
import time
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

        # Input variables
        self.mouse_press_last_timestamp = time.perf_counter()

        # ImGUI variables
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

        #imgui.end_frame()  # WHen to use this?
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def shutdown(self):
        for editor in self.editors:
            self.event_publisher.unsubscribe(listener=editor)
            editor.shutdown()

    def resize(self, width: int, height: int):
        self.imgui_renderer.resize(width, height)

    def files_dropped_event(self, x: int, y: int, paths: List[str]):
        self.logger.debug(f"Files dropped: {paths}")

    def key_event(self, key, action, modifiers):
        self.imgui_renderer.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui_renderer.mouse_position_event(x, y, dx, dy)

        y_gl = self.window_size[1] - y
        y_gui = y
        both_coordinates = (x, y_gl, y_gui)

        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_MOVE,
                                     event_data=both_coordinates,
                                     sender=self)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui_renderer.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui_renderer.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):

        y_gl = self.window_size[1] - y
        y_gui = y

        self.imgui_renderer.mouse_press_event(x, y, button)
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_PRESS,
                                     event_data=(button, x, y_gl, y_gui),
                                     sender=self)

        # Double click detection
        mouse_press_timestamp = time.perf_counter()
        time_between_clicks = mouse_press_timestamp - self.mouse_press_last_timestamp
        self.mouse_press_last_timestamp = mouse_press_timestamp

        if time_between_clicks < constants.DEFAULT_EDITOR_DOUBLE_CLICK_TIME_THRESHOLD:
            self.event_publisher.publish(event_type=constants.EVENT_MOUSE_DOUBLE_CLICK,
                                         event_data=(button, x, y),
                                         sender=self)

            # Three consecutive clicks may trigger two double clicks,
            # so we reset the timestamp after a double click
            self.mouse_press_last_timestamp = 0

        # Hide mouse cursor
        # TODO: Check this on how to handle disabled mouse:
        #       https://stackoverflow.com/questions/78013746/lock-mouse-inside-window-using-pythons-moderngl-window
        if button == constants.MOUSE_RIGHT:  # Assuming 2 is the right mouse button
            self.wnd.cursor = False

    def mouse_release_event(self, x: int, y: int, button: int):

        y_gl = self.window_size[1] - y
        y_gui = y

        self.imgui_renderer.mouse_release_event(x, y, button)
        self.event_publisher.publish(event_type=constants.EVENT_MOUSE_BUTTON_RELEASE,
                                     event_data=(button, x, y_gl, y_gui),
                                     sender=self)

        # Show mouse cursor
        # TODO: Check this on how to handle disabled mouse:
        #       https://stackoverflow.com/questions/78013746/lock-mouse-inside-window-using-pythons-moderngl-window
        if button == constants.MOUSE_RIGHT:  # Assuming 2 is the right mouse button
            self.wnd.cursor = True

    def key_event(self, key, action, modifiers):
        print(key, action, modifiers)
        if action == "ACTION_PRESS":
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_PRESS,
                                         event_data=(key, modifiers),
                                         sender=self)
            return

        if action == "ACTION_RELEASE":
            self.event_publisher.publish(event_type=constants.EVENT_KEYBOARD_RELEASE,
                                         event_data=(key, modifiers),
                                         sender=self)
            return

    def unicode_char_entered(self, char):
        self.imgui_renderer.unicode_char_entered(char)


if __name__ == '__main__':
    mglw.run_window_config(AppMglWnd)