import moderngl
import numpy as np
from typing import Any
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize

from src3 import constants
from src3 import math_3d
from src3.shader_loader import ShaderLoader
from src3.mesh_factory_3d import MeshFactory3D



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

        self.helper_fbo = self.ctx.framebuffer(
            depth_attachment=self.output_fbo.depth_attachment,
        )

        self.gizmo_scale = 1.0

    def calculate_scaled_model_matrix(self,
                                      camera_position: vec3,
                                      projection_matrix: mat4,
                                      model_matrix: mat4) -> mat4:

        # Determine the gizmo position
        gizmo_position = vec3(model_matrix[3])

        # Check if the projection is orthographic or perspective
        is_ortho = np.isclose(projection_matrix[3][3], 1.0, atol=1e-5)

        # Determine the distance factor
        if is_ortho:
            distance_factor = 1.0
        else:
            distance_factor = length(camera_position - gizmo_position)

        # Determine the scale factor to keep the gizmo a constant size on the screen
        viewport_height = self.output_fbo.viewport[3]
        proj_scale_y = 2.0 / projection_matrix[1][1]  # Assuming a standard projection matrix
        self.gizmo_scale = proj_scale_y * distance_factor * (constants.GIZMO_SIZE_ON_SCREEN_PIXELS / viewport_height)

        # Create a scale matrix
        scale_matrix = mat4(1.0)
        scale_matrix = scale(scale_matrix, vec3(self.gizmo_scale))

        # Apply the scale to the model matrix
        return model_matrix * scale_matrix

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4,
               component: Any):
        pass

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