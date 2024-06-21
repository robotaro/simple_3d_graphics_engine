import logging
import moderngl
from abc import ABC, abstractmethod

from src3 import constants
from src3.event_publisher import EventPublisher
from src3.shader_loader import ShaderLoader


class Editor(ABC):

    __slots__ = [
        "logger",
        "ctx",
        "params",
        "event_publisher",
        "shader_loader",
        "event_handlers"
    ]

    label = "editor_base"

    def __init__(self,
                 logger: logging.Logger,
                 ctx: moderngl.Context,
                 event_publisher: EventPublisher,
                 shader_loader: ShaderLoader,
                 params: dict):

        self.logger = logger
        self.ctx = ctx
        self.event_publisher = event_publisher
        self.shader_loader = shader_loader
        self.params = params if params is not None else {}
        self.event_handlers = self._assign_event_handlers()

    def _assign_event_handlers(self) -> dict:
        event_handlers = {}
        for attr in dir(self):
            if not attr.startswith("handle_event_"):
                continue

            event_name = attr[len("handle_event_"):].upper()
            event_constant = getattr(constants, f'EVENT_{event_name}', None)
            if event_constant:
                event_handlers[event_constant] = getattr(self, attr)
        return event_handlers

    def on_event(self, event_type: int, **kwargs):
        self.event_handlers[event_type](**kwargs)

    @abstractmethod
    def setup(self) -> bool:
        return True

    @abstractmethod
    def update(self, time: float, elapsed_time: float):
        pass

    @abstractmethod
    def shutdown(self):
        pass

    # ========================================================================
    #                           Event Handlers
    # ========================================================================

    def handle_event_keyboard_press(self, event_data: tuple):
        pass

    def handle_event_keyboard_release(self, event_data: tuple):
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