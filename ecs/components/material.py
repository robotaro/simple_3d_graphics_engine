from ecs.components.component import Component
import moderngl


class Material(Component):

    def __init__(self, **kwargs):
        self.diffuse = kwargs.get("diffuse", (0.85, 0.85, 0.85))
        self.ambient = kwargs.get("ambient", 0.5)
        self.specular = kwargs.get("specular", 0.5)
        self.alpha = kwargs.get("specular", 1.0)

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
