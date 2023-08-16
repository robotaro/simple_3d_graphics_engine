from ecs.components.component import Component


class Material(Component):

    def __init__(self):
        self.mode = None  # TODO: Add modes to the material rendering
        self.diffuse_color = (0.5, 0.5, 0.5)
        self.ambient = 0.5
        self.specular = 0.5
        self.alpha = 1.0
