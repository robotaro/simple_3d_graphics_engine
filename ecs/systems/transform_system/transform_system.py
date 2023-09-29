import numpy as np
import moderngl

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool


class TransformSystem(System):

    _type = "input_control_system"

    __slots__ = [
        "transforms"
    ]

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"],
                         component_pool=kwargs["component_pool"],
                         event_publisher=kwargs["event_publisher"])

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        for entity_uid, transform in self.component_pool.transform_3d_components.items():

            pass

        return True