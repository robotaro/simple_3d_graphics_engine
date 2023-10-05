import numpy as np
from ecs.math import mat4
from ecs.math import mat3
from ecs import constants

from ecs.components.component import Component


class Transform3D(Component):

    _type = "transform"

    __slots__ = [
        "world_matrix",
        "local_matrix",
        "position",
        "rotation",
        "look_at_target",
        "scale"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.world_matrix = np.eye(4, dtype=np.float32)
        self.local_matrix = np.eye(4, dtype=np.float32)

        self.position = kwargs.get("position", (0.0, 0.0, 0.0))
        self.rotation = kwargs.get("rotation", (0.0, 0.0, 0.0))
        self.scale = kwargs.get("rotation", (1.0, 1.0, 1.0))
