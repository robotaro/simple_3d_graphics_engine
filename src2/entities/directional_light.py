from src.core import constants
from src2.entities.entity import Entity
from src2.utilities import utils_params


class DirectionalLight(Entity):

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
        super().__init__(**kwargs)

        # Colors
        self.diffuse = utils_params.str2color(self.params.get("diffuse", (0.85, 0.85, 0.85)))
        self.specular = utils_params.str2color(self.params.get("specular", (1.0, 1.0, 1.0)))

        # Modifiers
        self.strength = self.params.get("strength", 1.0)

        # Moderngl variables
        self.shadow_texture = None

        # Flags
        self.shadow_enabled = self.params.get("shadow_enabled", True)
        self.enabled = self.params.get("enabled", True)

    def initialise(self, **kwargs) -> None:

        if self.ready_to_render:
            return

        ctx = kwargs["ctx"]

        self.shadow_texture = ctx.depth_texture(size=constants.DIRECTIONAL_LIGHT_TEXTURE_SIZE)

        self.ready_to_render_flag = True

    def release(self):

        if self.shadow_texture is not None:
            self.shadow_texture.release()
