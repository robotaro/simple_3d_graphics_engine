import logging
from typing import Any

class EventPublisher:

    __slots__ = [
        "logger",
        "listeners"
    ]

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.listeners = []

    def subscribe(self, listener: Any):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def publish(self, event_type: int, sender, **kwargs) -> None:
        """
        Publishes an event to all the listeners. Make sure to specify a sender if a subsystem is sending it
        to avoid it accidentally receiving its own message and creating a infinite loop.

        :param event_type: int, event ID defined in constants.py
        :param sender: sender needs to sent its own reference to avoid unwanted loops event loops
        :return: None
        """

        for listener in self.listeners:

            # Prevent a sender to publishing to itself and creating a potential infinite loop
            if sender == listener:
                continue

            listener.on_event(event_type=event_type, **kwargs)
