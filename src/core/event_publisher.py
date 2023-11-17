import logging

from src.core import constants


class EventPublisher:

    __slots__ = [
        "logger",
        "listeners"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger

        # Do it manually here to avoid having to check at every publish() call
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
            constants.EVENT_PROFILING_SYSTEM_PERIODS: []
        }

    def subscribe(self, event_type: int, listener):
        self.listeners[event_type].append(listener)

    def unsubscribe(self, event_type, listener):
        if listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)

    def publish(self, event_type, event_data: tuple, sender):
        """
        Publishes an event to all the listeners. Make sure to specify a sender if a subsystem is sending it
        to avoid it accidentally receiving its own message and creating a infinite loop.

        :param event_type:
        :param event_data:
        :param sender:
        :return:
        """

        for listener in self.listeners[event_type]:

            # Prevent a sender to publishing to itself and creating a potential infinite loop
            if sender == listener:
                continue

            listener.on_event(event_type=event_type, event_data=event_data)
