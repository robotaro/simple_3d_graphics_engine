from vao import VAO
from texture import Texture


class Mesh:
    def __init__(self, app):
        self.app = app
        self.vao = VAO(app.context)
        self.texture = Texture(app.context)

    def destroy(self):
        self.vao.destroy()
        self.texture.destroy()