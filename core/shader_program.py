

class ShaderProgram:

    def __init__(self, ctx, shader_program_name: str):
        self.ctx = ctx
        with open(f'shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        self.program = self.ctx.program(vertex_shader=vertex_shader,
                                        fragment_shader=fragment_shader)

    def destroy(self):
        self.program.release()

