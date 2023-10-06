from ecs.components.component import Component
from ecs import constants


class Material(Component):

    _type = constants.COMPONENT_TYPE_MESH  # TODO: I think I don't need to set the type as I can use the class itself

    def __init__(self, **kwargs):
        
        super().__init__()

        # Colors
        self.diffuse = kwargs.get("diffuse", (0.85, 0.85, 0.85))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))

        # Factors
        self.shininess_factor = kwargs.get("shininess_factor", 32.0)
        self.metalic_factor = kwargs.get("metalic_factor", 0.0)
        self.roughness_factor = kwargs.get("roughness_factor", 1.0)

        # Render modes
        self.color_source = constants.RENDER_MODE_COLOR_SOURCE_SINGLE
        self.lighting_mode = constants.RENDER_MODE_LIGHTING_LIT

        # Transparency
        self.alpha = kwargs.get("alpha", 1.0)

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
