import glm

class Light:
    def __init__(self, position=(0, 30, 10), color=(1, 1, 1)):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        self.ambient = 0.06 * self.color
        self.diffuse = 0.8 * self.color
        self.specular = 1.0 * self.color