import numpy as np

import _simple_2d_example


class Example(_simple_2d_example.Example):
    title = 'Color Triangle using two buffers'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # the shader program is inherited
        # self.prog = self.ctx.program(...)
        self.prog['RenderMode'] = self.ATTRIB_COLOR_MODE

        vertices = np.array([
            # x, y
            0.0, 0.8,
            -0.6, -0.8,
            0.6, -0.8,
        ])

        colors = np.array([
            # red, green, blue
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ])

        self.vbo1 = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vbo2 = self.ctx.buffer(colors.astype('f4').tobytes())

        self.vao = self.ctx.vertex_array(self.prog, [
            self.vbo1.bind('in_vert', layout='2f'),
            self.vbo2.bind('in_color', layout='3f'),
        ])

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
