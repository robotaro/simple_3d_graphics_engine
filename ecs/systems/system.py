import moderngl
from ecs.entity_manager import EntityManager


class System:

    _type = "base_system"

    def __init__(self):
        pass

    def initialize(self) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               entity_manager: EntityManager,
               context: moderngl.Context,
               event=None):
        pass

    def shutdown(self):
        pass