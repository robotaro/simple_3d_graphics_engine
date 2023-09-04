from ecs.components.component import Component
import moderngl


class Material(Component):

    def __init__(self, **kwargs):
        self.albedo = kwargs.get("albedo", (0.85, 0.85, 0.85))  # Albedo is the base color
        self.diffuse_factor = kwargs.get("diffuse_factor", 0.5)
        self.ambient_factor = kwargs.get("ambient_factor", 0.5)
        self.specular_factor = kwargs.get("specular_factor", 0.5)
        self.alpha = kwargs.get("specular", 1.0)

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
