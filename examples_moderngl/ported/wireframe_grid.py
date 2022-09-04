import numpy as np
import moderngl

import _simple_3d_example


def grid(size, steps):
    u = np.repeat(np.linspace(-size, size, steps), 2)
    v = np.tile([-size, size], steps)
    w = np.zeros(steps * 2)
    return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])


class Example(_simple_3d_example.Example):
    title = 'Hello World'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # the shader program is inherited
        # self.prog = self.ctx.program(...)

        self.vbo = self.ctx.buffer(grid(2.0, 10).astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.prog['Color'] = (0.0, 0.0, 0.0)
        self.set_camera(fov=60.0, eye=(4, 3, 2), target=(0, 0, 0))
        self.vao.render(moderngl.LINES)


if __name__ == '__main__':
    Example.run()
