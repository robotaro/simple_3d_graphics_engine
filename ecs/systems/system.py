import logging
import moderngl
from collections import deque

from ecs.component_pool import ComponentPool
from ecs.event_publisher import EventPublisher
from ecs.action_publisher import ActionPublisher


class System:

    __slots__ = [
        "logger",
        "event_publisher",
        "action_publisher",
        "component_pool",
        "action_queue",
        "current_action",
        "runtime"
    ]

    _type = "base_system"

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher):
        self.logger = logger
        self.event_publisher = event_publisher
        self.action_publisher = action_publisher
        self.action_queue = deque()
        self.current_action = None
        self.component_pool = component_pool
        self.runtime = 0.0

    def on_event(self, event_type: int, event_data: tuple):
        pass

    def on_action(self, action_type: int, action_data: tuple, entity_id: int, component_type: int):
        self.action_queue.appendleft((action_type, action_data, entity_id, component_type))

    def select_action(self) -> bool:
        """
        Returns false if there are no more actions to execute
        """
        if self.current_action is None:
            self.current_action = self.action_queue.pop()
        return self.current_action is not None

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               context: moderngl.Context) -> bool:
        return True

    def shutdown(self):
        pass
