from vbo import VBO
from shader_program import ShaderProgram


class VAO:
    def __init__(self, context, vbo: VBO, shader_program: ShaderProgram):
        self.context = context
        self.vbo = vbo
        self.shader_program = shader_program
        self.vao = self.context.vertex_array(shader_program, [(vbo.vbo, vbo.format, *vbo.attributes)])

    def destroy(self):
        self.vbo.destroy()