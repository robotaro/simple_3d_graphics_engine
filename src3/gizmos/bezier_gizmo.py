import moderngl
import numpy as np
from src3 import constants
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize
import copy

from src3 import math_3d
from src3.shader_loader import ShaderLoader


class BezierGizmo:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 output_fbo: moderngl.Framebuffer):

        self.active_handle_index = -1
        self.handle_world_matrix = mat4(1.0)

    def generate_vbos_and_vaos(self):

        pass

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4):
        pass