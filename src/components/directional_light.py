from src import constants
from src.components.component import Component


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

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        # Colors
        self.diffuse = Component.dict2color(input_dict=self.parameters, key="diffuse", default_value=(0.85, 0.85, 0.85))
        self.specular = Component.dict2color(input_dict=self.parameters, key="specular", default_value=(1.0, 1.0, 1.0))

        # Modifiers
        self.strength = Component.dict2float(input_dict=self.parameters, key="strength", default_value=1.0)

        # Moderngl variables
        self.shadow_texture = None

        # Flags
        self.shadow_enabled = Component.dict2bool(input_dict=self.parameters, key="shadow_enabled", default_value=True)
        self.enabled = Component.dict2bool(input_dict=self.parameters, key="enabled", default_value=True)

    def initialise(self, **kwargs) -> None:

        if self.initialised:
            return

        ctx = kwargs["ctx"]

        self.shadow_texture = ctx.depth_texture(size=constants.DIRECTIONAL_LIGHT_SIZE)

        self.initialised = True

    def release(self):

        if self.shadow_texture is not None:
            self.shadow_texture.release()
