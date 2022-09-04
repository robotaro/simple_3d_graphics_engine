import numpy as np

import _example


class Example(_example.Example):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;

                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                out vec4 f_color;

                void main() {
                    f_color = vec4(0.2, 0.4, 0.7, 1.0);
                }
            ''',
        )

        vertices = np.array([
            0.0, 0.8,
            -0.6, -0.8,
            0.6, -0.8,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
