import numpy as np

from ecs import constants
from ecs.components.component import Component


class PointLight(Component):

    _type = constants.COMPONENT_TYPE_SPOT_LIGHT

    def __init__(self, **kwargs):
        self.color = (0.5, 0.5, 0.5)
        self.position = kwargs.get("position", np.array((50, 10, 50), dtype=np.float32))
        self.specular = 0.5