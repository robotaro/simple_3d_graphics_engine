from PIL import Image
import numpy as np
from objloader import Obj

import _simple_3d_example
import moderngl


class Example(_simple_3d_example.Example):
    title = 'Hello World'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # the shader program is inherited
        # self.prog = self.ctx.program(...)
        self.prog['RenderMode'] = self.TEXTURE_WITH_LIGHT_MODE

        obj = Obj.open('examples/data/crate.obj')
        img = Image.open('examples/data/crate.png')
        self.texture = self.ctx.texture(img.size, 3, img.tobytes('raw', 'RGB', 0, -1))
        self.sampler = self.ctx.sampler(texture=self.texture)

        self.vbo = self.ctx.buffer(obj.pack('vx vy vz nx ny nz tx ty'))
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert', 'in_norm', 'in_text')
        self.vao.scope = self.ctx.scope(enable=self.ctx.DEPTH_TEST, samplers=[
            self.sampler.assign(0),
        ])

    def render(self, time: float, frame_time: float):
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.set_camera(fov=60.0, eye=(4, 3, 2), target=(0, 0, 0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
