from ecs.components.component import Component
import moderngl


class Material(Component):

    def __init__(self, **kwargs):

        # Colors
        self.diffuse = kwargs.get("diffuse", (0.85, 0.85, 0.85))
        self.specular = kwargs.get("specular", (1.0, 1.0, 1.0))

        # Factors
        self.shininess_factor = kwargs.get("shininess_factor", 32.0)
        self.metalic_factor = kwargs.get("metalic_factor", 0.0)
        self.roughness_factor = kwargs.get("roughness_factor", 1.0)

        # Transparency
        self.alpha = kwargs.get("alpha", 1.0)

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
