import numpy as np
import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.math import mat4


class DirectionalLight(Component):

    __slots__ = [
        "diffuse",
        "ambient",
        "specular",
        "strength",
        "shadow_texture",
        "shadow_enabled",
        "enabled"
    ]

    def __init__(self, **kwargs):
        
        super().__init__()

        # Colors
        self.diffuse = kwargs.get("diffuse", (1.0, 1.0, 1.0))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))

        # Modifiers
        self.strength = kwargs.get("strength", 1.0)

        # Moderngl variables
        self.shadow_texture = None

        # Flags
        self.shadow_enabled = kwargs.get("shadow_enabled", True)
        self.enabled = kwargs.get("enabled", True)

    def initialise(self, **kwargs) -> None:

        ctx = kwargs["ctx"]

        if self.initialised:
            return

        self.shadow_texture = ctx.depth_texture(size=constants.DIRECTIONAL_LIGHT_SIZE)

    def release(self):

        if self.shadow_texture is not None:
            self.shadow_texture.release()
