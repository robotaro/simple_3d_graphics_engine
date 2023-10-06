import numpy as np
import moderngl
import logging

from ecs.component_pool import ComponentPool
from ecs.systems.system import System
from ecs.event_publisher import EventPublisher
from ecs.action_publisher import ActionPublisher
from ecs.math import mat4


class TransformSystem(System):

    _type = "transform_system"

    def __init__(self, logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher)

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        for entity_uid, transform in self.component_pool.transform_3d_components.items():

            if not transform.dirty:
                continue

            transform.world_matrix = mat4.compute_transform(position=transform.position,
                                                            rotation_rad=transform.rotation,
                                                            scale=transform.scale[0])
            transform.dirty = False

        # ================= Process actions =================

        self.select_next_action()
        if self.current_action is None:
            return True

        return True