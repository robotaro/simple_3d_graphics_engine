
import numpy as np
import moderngl

from src3 import constants
from src3.shader_loader import ShaderLoader


class PointCloudComponent:

    __slots__ = [
        "ctx",
        "shader_loader",
        "program",
        "vertex_vbo",
        "color_vbo",
        "vao",
        "num_points"
    ]

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 points: np.ndarray,
                 colors: np.ndarray):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.program = shader_loader.get_program("points.glsl")
        self.vertex_vbo = self.ctx.buffer(points.tobytes())
        self.color_vbo = self.ctx.buffer(colors.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vertex_vbo, '3f', 'in_position'),
                (self.color_vbo, '3f', 'in_color'),
            ]
        )

        self.num_points = points.shape[0]

    def render(self):
        self.vao.render(mode=moderngl.POINTS)

    def release(self):
        if self.vertex_vbo:
            self.vertex_vbo.release()
        if self.color_vbo:
            self.color_vbo.release()
        if self.vao:
            self.vao.release()