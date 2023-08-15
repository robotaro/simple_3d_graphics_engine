import numpy as np

from ecs.components.component import Component


class Transform(Component):

    _type = "transform"

    def __init__(self, **kwargs):
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.local_matrix = np.eye(4, dtype=np.float32)

        self.position = kwargs.get("position", np.zeros((3,), dtype=np.float32))
        self.rotation = kwargs.get("rotation", np.zeros((3,), dtype=np.float32))
        self.scale = kwargs.get("scale", np.ones((3,), dtype=np.float32))
        self._dirty_flag = True
