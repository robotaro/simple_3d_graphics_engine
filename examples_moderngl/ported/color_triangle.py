import numpy as np

import _simple_2d_example


class Example(_simple_2d_example.Example):
    title = 'Color Triangle'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # the shader program is inherited
        # self.prog = self.ctx.program(...)
        self.prog['RenderMode'] = self.ATTRIB_COLOR_MODE

        vertices = np.array([
            # x, y, red, green, blue
            0.0, 0.8, 1.0, 0.0, 0.0,
            -0.6, -0.8, 0.0, 1.0, 0.0,
            0.6, -0.8, 0.0, 0.0, 1.0,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
