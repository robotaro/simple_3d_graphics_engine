import logging
import moderngl
import time

from ecs.component_pool import ComponentPool


class System:

    __slots__ = [
        "logger",
        "event_publisher",
        "runtime"
    ]

    _type = "base_system"

    def __init__(self, logger: logging.Logger, event_publisher):
        self.logger = logger
        self.event_publisher = event_publisher
        self.runtime = 0.0  # Initialize the attribute

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               component_pool: ComponentPool,
               context: moderngl.Context):
        pass

    def on_event(self, event_type: int, event_data: tuple):
        pass

    def shutdown(self):
        pass
