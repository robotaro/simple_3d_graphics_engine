import numpy as np
from core.math import mat4

from ecs.components.component import Component


class Transform(Component):

    _type = "transform"

    __slots__ = [
        "world_matrix",
        "local_matrix",
        "position",
        "rotation",
        "scale"
    ]

    def __init__(self, **kwargs):
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.local_matrix = np.eye(4, dtype=np.float32)

        self.position = kwargs.get("position", np.zeros((3,), dtype=np.float32))
        self.rotation = kwargs.get("rotation", np.zeros((3,), dtype=np.float32))
        self.scale = kwargs.get("scale", 1.0)
        self._dirty_flag = True

    def update(self):

        self.local_matrix = mat4.compute_transform(position=self.position,
                                                   rotation_rad=self.rotation,
                                                   scale=self.scale)
