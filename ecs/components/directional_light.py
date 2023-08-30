import numpy as np

from ecs.components.component import Component
from ecs.math import mat4


class DirectionalLight(Component):

    def __init__(self, **kwargs):
        self.color = (0.5, 0.5, 0.5)
        self.position = kwargs.get("position", np.array((50, 10, 50), dtype=np.float32))
        self.direction = kwargs.get("direction", np.array((-1, -1, 0), dtype=np.float32))
        self.specular = 0.5

    def get_view_matrix(self):
        return mat4.look_at_direction(
            position=self.position,
            direction=self.direction,
            up=np.array((0, 1, 0), dtype=np.float32))