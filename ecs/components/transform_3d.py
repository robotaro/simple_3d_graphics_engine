import numpy as np

from ecs.components.component import Component


class Transform3D(Component):

    _type = "transform"

    __slots__ = [
        "world_matrix",
        "local_matrix",
        "position",
        "rotation",
        "scale",
        "dirty"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.world_matrix = np.eye(4, dtype=np.float32)

        self.position = kwargs.get("position", (0.0, 0.0, 0.0))
        self.rotation = kwargs.get("rotation", (0.0, 0.0, 0.0))
        self.scale = kwargs.get("scale", (1.0, 1.0, 1.0))
        self.dirty = True

    def move(self, delta_position: np.array):
        self.position += delta_position
        self.dirty = True

    def rotate(self, delta_rotation: np.array):
        self.rotation += delta_rotation
        self.dirty = True

    def set_position(self, position: tuple):
        self.position = position
        self.dirty = True

    def set_rotation(self, position: tuple):
        self.position = position
        self.dirty = True
