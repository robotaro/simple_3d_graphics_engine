import numpy as np

from ecs import constants
from ecs.components.component import Component
from ecs.math import mat4


class DirectionalLight(Component):

    __slots__ = [
        "diffuse",
        "ambient",
        "specular",
        "strength",
        "shadow_enabled",
        "enabled"
    ]

    def __init__(self, **kwargs):

        # Colors
        self.diffuse = kwargs.get("diffuse", (1.0, 1.0, 1.0))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))

        # Modifiers
        self.strength = kwargs.get("strength", 1.0)

        # Flags
        self.shadow_enabled = kwargs.get("shadow_enabled", True)
        self.enabled = kwargs.get("enabled", True)
