import numpy as np
import moderngl

from ecs import constants
from ecs.systems.system import System
from ecs.math import intersection_3d
from ecs.utilities import utils_camera
from ecs.math import mat4


class TransformSystem(System):

    _type = "gizmo_system"

    __slots__ = [
        "entity_ray_intersection_list",
        "window_size"
    ]

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"],
                         component_pool=kwargs["component_pool"],
                         event_publisher=kwargs["event_publisher"])

        self.window_size = None
        self.entity_ray_intersection_list = []

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:


        for entity_uid, transform in self.component_pool.transform_3d_components.items():


            # TODO: Add the _dirty_flag check to avoid unecessary updates
            transform.local_matrix = mat4.compute_transform(position=transform.position,
                                                            rotation_rad=transform.rotation,
                                                            scale=transform.scale)

            pass

        # ================= Process actions =================
        if not self.select_action():
            return True

        return True