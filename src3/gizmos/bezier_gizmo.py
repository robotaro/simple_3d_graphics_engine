from typing import Any
import moderngl
import numpy as np
from src3 import constants
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize
import copy

from src3.gizmos.gizmo import Gizmo
from src3 import math_3d
from src3.components.bezier_segment_component import BezierSegmentComponent


class BezierGizmo(Gizmo):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

        self.active_handle_index = -1
        self.line_width = 3.0
        self.line_color = vec4(1, 0.5, 0, 1)

        self.control_points_vertices_vbo = None
        self.control_points_colors_vbo = None
        self.control_points_vao = None
        self.curve_vbo = None
        self.curve_vao = None

        self.generate_vbos_and_vaos()

    def generate_vbos_and_vaos(self):

        dummy_vertices = np.ones((4, 3), dtype='f4') * 0.5
        self.control_points_vertices_vbo = self.ctx.buffer(dummy_vertices.tobytes())

        dummy_colors = np.ones((4, 3), dtype='f4')
        self.control_points_colors_vbo = self.ctx.buffer(dummy_colors.tobytes())

        self.control_points_vao = self.ctx.vertex_array(
            self.program_points,
            [
                (self.control_points_vertices_vbo, '3f', 'in_position'),
                (self.control_points_colors_vbo, '3f', 'in_color')
            ]
        )

        self.curve_vbo = self.ctx.buffer(reserve=4096, dynamic=True)
        self.curve_vao = self.ctx.simple_vertex_array(
                self.program_lines,
                self.curve_vbo,
                'aPositionSize',
                'aColor')

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4,
               component: Any):

        # Update lines VBOs
        if not isinstance(component, BezierSegmentComponent):
            return

        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND)

        # ==========[ Render Lines Between Control Points ]=============

        mvp = projection_matrix * view_matrix * model_matrix
        self.program_lines['uViewProjMatrix'].write(mvp)

        self.curve_vao.render(moderngl.LINES)

        # ==========[ Render Control Points ]=============

        self.ctx.enable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = 'auto'

        # Bind the helper framebuffer to clear the depth buffer
        self.helper_fbo.use()
        self.helper_fbo.clear(depth=True)

        # Bind the output framebuffer to render the gizmo
        self.output_fbo.use()

        # TODO: Put this in the UBO
        #self.program_points['cam_pos'].write(vec3(inverse(view_matrix)[3]))

        self.control_points_vao.render(moderngl.POINTS)

        self.ctx.disable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = None

    def update_selection(self, component: BezierSegmentComponent):
        """
        This function should be called when the component is updated
        :param component:
        :return:
        """

        if component is None:
            return

        # Update current vbos
        points = component.interpolate_points(t_values=component.t_values)
        a = np.array([self.line_width,
                      self.line_color.x,
                      self.line_color.y,
                      self.line_color.z,
                      self.line_color.w], dtype='f4').reshape(-1, 5)
        size_and_colors = np.tile(a, (points.shape[0], 1))

        vertex_data = np.concatenate([points, size_and_colors], axis=1)
        self.curve_vbo.write(vertex_data.tobytes())
        self.control_points_vertices_vbo.write(component.control_points.tobytes())

    def handle_event_mouse_button_press(self,
                                        button: int,
                                        ray_origin: vec3,
                                        ray_direction: vec3,
                                        model_matrix: mat4,
                                        component: Any) -> mat4:

        # If the

        return None

    def handle_event_mouse_move(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:

        if not isinstance(component, BezierSegmentComponent):
            return None

        # Calculate perpendicular distances between handles and ray
        handles_dist2 = [math_3d.distance2_ray_point(ray_origin=ray_origin,
                                                     ray_direction=ray_direction,
                                                     point=vec3(point)) for point in component.control_points]

        # TODO: Continue from here (B)

        #if handles_dist2 < (self.gizmo_scale * constants.GIZMO_CENTER_RADIUS) ** 2:
        #    pass


        return None

    def handle_event_mouse_drag(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:
        if component is None:
            return None

        return None