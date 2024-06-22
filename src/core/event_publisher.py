import logging
from typing import Any
from src.core import constants


class EventPublisher:

    __slots__ = [
        "logger",
        "listeners"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger

        self.listeners = {
            constants.EVENT_KEYBOARD_PRESS: [],
            constants.EVENT_KEYBOARD_RELEASE: [],
            constants.EVENT_KEYBOARD_REPEAT: [],
            constants.EVENT_MOUSE_ENTER_UI: [],
            constants.EVENT_MOUSE_LEAVE_UI: [],
            constants.EVENT_MOUSE_BUTTON_PRESS: [],
            constants.EVENT_MOUSE_BUTTON_RELEASE: [],
            constants.EVENT_MOUSE_DOUBLE_CLICK: [],
            constants.EVENT_MOUSE_MOVE: [],
            constants.EVENT_MOUSE_SCROLL: [],
            constants.EVENT_WINDOW_SIZE: [],
            constants.EVENT_WINDOW_FRAMEBUFFER_SIZE: [],
            constants.EVENT_WINDOW_DROP_FILES: [],
            constants.EVENT_ENTITY_SELECTED: [],
            constants.EVENT_ENTITY_DESELECTED: [],
            constants.EVENT_MOUSE_ENTER_GIZMO_3D: [],
            constants.EVENT_MOUSE_LEAVE_GIZMO_3D: [],
            constants.EVENT_MOUSE_GIZMO_3D_ACTIVATED: [],
            constants.EVENT_MOUSE_GIZMO_3D_DEACTIVATED: [],
            constants.EVENT_PROFILING_SYSTEM_PERIODS: [],
            constants.EVENT_GIZMO_3D_SYSTEM_PARAMETER_UPDATED: [],
            constants.EVENT_RENDER_SYSTEM_PARAMETER_UPDATED: [],
        }

    def subscribe(self, event_type: int, listener: Any):
        if event_type not in self.listeners:
            raise KeyError(f"[ERROR] Failed to subscribe to event. Event '{event_type}' "
                           f"does not exist. Please check spelling.")
        self.listeners[event_type].append(listener)

    def unsubscribe(self, event_type, listener):
        if listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)

    def publish(self, event_type: int, event_data: tuple, sender) -> None:
        """
        Publishes an event to all the listeners. Make sure to specify a sender if a subsystem is sending it
        to avoid it accidentally receiving its own message and creating a infinite loop.

        :param event_type: int, event ID defined in constants.py
        :param event_data: tuple, variable type of data inside, but no tuples inside this tuple!
        :param sender: sender needs to sent its own reference to avoid unwanted loops event loops
        :return: None
        """

        for listener in self.listeners[event_type]:

            # Prevent a sender to publishing to itself and creating a potential infinite loop
            if sender == listener:
                continue

            listener.on_event(event_type=event_type, event_data=event_data)
