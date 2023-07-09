


class Mesh:
    def __init__(self, ):
        self.vao = vao
        self.texture = texture

    def destroy(self):
        self.vao.destroy()
        self.texture.destroy()