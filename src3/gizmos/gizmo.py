import moderngl

from typing import Any
from src3 import math_3d
from src3.shader_loader import ShaderLoader
from src3.mesh_factory_3d import MeshFactory3D
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize


class Gizmo:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 output_fbo: moderngl.Framebuffer):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.output_fbo = output_fbo
        self.program_lines = shader_loader.get_program("gizmo_lines.glsl")
        self.program_triangles = shader_loader.get_program("gizmo_triangles.glsl")

        self.gizmo_scale = 1.0

    def handle_event_mouse_button_press(self,
                                        button: int,
                                        ray_origin: vec3,
                                        ray_direction: vec3,
                                        model_matrix: mat4,
                                        component: Any):

        pass

    def handle_event_mouse_button_release(self,
                                          button: int,
                                          ray_origin: vec3,
                                          ray_direction: vec3,
                                          model_matrix: mat4,
                                          component: Any):

        pass

    def handle_event_keyboard_press(self, event_data: tuple) -> mat4:
        key, modifiers = event_data
        return None

    def handle_event_keyboard_release(self, event_data: tuple) -> mat4:
        key, modifiers = event_data
        return None

    def handle_event_mouse_move(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:

        return None

    def handle_event_mouse_drag(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:

        return None