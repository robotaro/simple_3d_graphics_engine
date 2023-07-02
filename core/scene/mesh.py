from vao import VAO
from texture import Texture


class Mesh:
    def __init__(self, vao: VAO, texture: Texture):
        self.vao = vao
        self.texture = texture

    def destroy(self):
        self.vao.destroy()
        self.texture.destroy()