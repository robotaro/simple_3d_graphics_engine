import numpy as np

import _example


class Example(_example.Example):
    title = 'Program Uniforms'
    window_size = (400, 400)
    aspect_ratio = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 WindowSize;

                in vec2 in_vert;

                void main() {
                    gl_Position = vec4(in_vert / WindowSize * 2.0 - 1.0, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                uniform vec3 Color;

                out vec4 f_color;

                void main() {
                    f_color = vec4(Color, 1.0);
                }
            ''',
        )

        self.prog['WindowSize'] = self.window_size
        self.prog['Color'] = (0.2, 0.4, 0.7)

        vertices = np.array([
            100.0, 100.0,
            300.0, 200.0,
            200.0, 300.0,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
