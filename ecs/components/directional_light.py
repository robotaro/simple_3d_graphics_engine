from ecs.components.component import Component


class DirectionalLight(Component):

    def __init__(self):
        self.color = (0.5, 0.5, 0.5)
        self.direction = 0.5
        self.specular = 0.5
        self.alpha = 1.0
