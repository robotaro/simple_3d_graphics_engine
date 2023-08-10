from ecs import constants
from systems.system import System


class EventPublisher:

    __slots__ = ["listeners"]

    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type: int, listener):
        # Create a new event type if not already here
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        # Add listener to list of that particular event
        self.listeners[event_type].append(listener)

    def unsubscribe(self, event_type, listener: System):
        if listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)

    def publish(self, event_type, event_data):
        for listener in self.listeners[event_type]:
            listener.on_event(event_type=event_type, event_data=event_data)