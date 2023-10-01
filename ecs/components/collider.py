import numpy as np
import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.math import intersection_3d


class Collider(Component):

    """
    Colliders are components that will allow collision tobe detected between
    """

    _type = "collision_body"

    __slots__ = [
        "shape",
        "layer",
        "radius"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.shape = kwargs.get("shape", "sphere")
        self.layer = 0

        self.radius = kwargs.get("radius", 1.0)

    def ray_intersection_boolean(self, ray_origin: np.array, ray_direction: np.array) -> bool:

        pass




