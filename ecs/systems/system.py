import moderngl

from ecs.component_pool import ComponentPool


class System:

    def __init__(self):
        self.logger = None

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               entity_manager: ComponentPool,
               context: moderngl.Context):
        pass

    def on_event(self, event_type: int, event_data: tuple):
        pass

    def shutdown(self):
        pass