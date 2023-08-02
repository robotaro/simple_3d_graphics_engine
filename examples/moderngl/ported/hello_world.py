import numpy as np

import _simple_2d_example


class Example(_simple_2d_example.Example):
    title = 'Hello World'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # the shader program is inherited
        # self.prog = self.ctx.program(...)

        vertices = np.array([
            0.0, 0.8,
            -0.6, -0.8,
            0.6, -0.8,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time: float, frame_time: float):
        self.ctx.clear(1.0, 1.0, 1.0)
        self.prog['Color'] = 0.2, 0.4, 0.7
        self.vao.render()


if __name__ == '__main__':
    Example.run()
