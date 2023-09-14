import numpy as np

from ecs import constants
from ecs.components.component import Component


class PointLight(Component):

    __slots__ = [
        "position",
        "diffuse",
        "ambient",
        "specular",
        "intensity",
        "attenuation_coeffs",
        "active"
    ]

    _type = constants.COMPONENT_TYPE_SPOT_LIGHT

    def __init__(self, **kwargs):
        self.position = kwargs.get("position", (50, 10, 50))
        self.diffuse = kwargs.get("diffuse", (1.0, 1.0, 1.0))
        self.ambient = kwargs.get("ambient", (1.0, 1.0, 1.0))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))
        self.attenuation_coeffs = kwargs.get("attenuation_coeffs", (0.1, 0.01, 0.001))
        self.intensity = kwargs.get("intensity", 0.8)
        self.active = True
