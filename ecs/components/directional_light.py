import numpy as np

from ecs import constants
from ecs.components.component import Component
from ecs.math import mat4


class DirectionalLight(Component):

    def __init__(self, **kwargs):
        self.diffuse = kwargs.get("diffuse", (1.0, 1.0, 1.0))
        self.ambient = kwargs.get("ambient", (1.0, 1.0, 1.0))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))
        self.strength = kwargs.get("strength", 1.0)