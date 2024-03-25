import logging
import moderngl

from src2.core import constants
from src2.core.event_publisher import EventPublisher
from src2.core.shader_program_library import ShaderProgramLibrary
from src.core.data_manager import DataManager


class Editor:

    __slots__ = [
        "logger",
        "ctx",
        "params",
        "event_publisher",
        "data_manager",
        "scene",
        "shader_library",
        "current_action",
        "event_handlers",
        "active"
    ]

    label = "base_module"

    def __init__(self,
                 logger: logging.Logger,
                 ctx: moderngl.Context,
                 event_publisher: EventPublisher,
                 data_manager: DataManager,
                 shader_library: ShaderProgramLibrary,
                 params: dict):

        self.logger = logger
        self.ctx = ctx
        self.event_publisher = event_publisher
        self.data_manager = data_manager
        self.shader_library = shader_library
        self.params = params if params is not None else {}
        self.active = True

        # Dynamically build the event_handlers dictionary
        self.event_handlers = {}
        for attr in dir(self):
            if attr.startswith("handle_event_"):
                event_name = attr[len("handle_event_"):].upper()
                event_constant = getattr(constants, f'EVENT_{event_name}', None)
                if event_constant:
                    self.event_handlers[event_constant] = getattr(self, attr)

    def on_event(self, event_type: int, **kwargs):
        self.event_handlers[event_type](**kwargs)

    def on_imgui_top_menu(self):
        pass

    def on_imgui_window(self):
        pass

    def update(self, elapsed_time: float) -> bool:
        return True

    def shutdown(self):
        pass

    # ========================================================================
    #                         Event callbacks
    # ========================================================================

    def handle_event_keyboard_press(self, key, scancode, mods):
        pass

    def handle_event_keyboard_release(self, key, scancode, mods):
        pass

    def handle_event_keyboard_repeat(self, event_data: tuple):
        pass

    def handle_event_mouse_enter_ui(self, event_data: tuple):
        pass

    def handle_event_mouse_leave_ui(self, event_data: tuple):
        pass

    def handle_event_mouse_button_press(self, event_data: tuple):
        pass

    def handle_event_mouse_button_release(self, event_data: tuple):
        pass

    def handle_event_mouse_double_click(self, event_data: tuple):
        pass

    def handle_event_mouse_move(self, event_data: tuple):
        pass

    def handle_event_mouse_scroll(self, event_data: tuple):
        pass

    def handle_event_window_size(self, event_data: tuple):
        pass

    def handle_event_window_framebuffer_size(self, event_data: tuple):
        pass

    def handle_event_window_drop_files(self, event_data: tuple):
        pass

    def handle_event_entity_selected(self, event_data: tuple):
        pass

    def handle_event_entity_deselected(self, event_data: tuple):
        pass

    def handle_event_mouse_enter_gizmo_3d(self, event_data: tuple):
        pass

    def handle_event_mouse_leave_gizmo_3d(self, event_data: tuple):
        pass

    def handle_event_mouse_gizmo_3d_activated(self, event_data: tuple):
        pass

    def handle_event_mouse_gizmo_3d_deactivated(self, event_data: tuple):
        pass

    def handle_event_profiling_system_periods(self, event_data: tuple):
        pass

    def handle_event_gizmo_3d_system_parameter_updated(self, event_data: tuple):
        pass

    def handle_event_render_system_parameter_updated(self, event_data: tuple):
        pass