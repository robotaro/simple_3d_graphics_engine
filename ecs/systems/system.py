import moderngl

from ecs.entity_manager import EntityManager


class System:

    def __init__(self):
        self.logger = None

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               entity_manager: EntityManager,
               context: moderngl.Context):
        pass

    def on_event(self, event_type: int, event_data: tuple):
        pass

    def shutdown(self):
        pass