import time

import moderngl
import numpy as np
from src3 import constants
from glm import vec3, vec4, mat4, length, length2, inverse, translate

from src3 import math_3d
from src3.shader_loader import ShaderLoader


class Gizmo3D:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 output_fbo: moderngl.Framebuffer,
                 gizmo_size_on_screen=0.1):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.output_fbo = output_fbo
        self.program = shader_loader.get_program("gizmo_shader.glsl")

        self.gizmo_size_on_screen = gizmo_size_on_screen

        self.helper_fbo = self.ctx.framebuffer(
            depth_attachment=self.output_fbo.depth_attachment,
        )

        self.translation_vao = None
        self.translation_vbo = None
        self.generate_translation_vertices()

        self.plane_axis_list = [(0, 1), (0, 2), (1, 2)]

        self.gizmo_scale = 1.0
        self.gizmo_mode = constants.GIZMO_MODE_TRANSLATION
        self.state = constants.GIZMO_STATE_INACTIVE
        self.active_axis_index = -1
        self.active_plane_index = -1
        self.gizmo_translation_offset_point = vec3(0, 0, 0)
        self.ray_to_axis_dist2 = [0.0] * 3  # Closest distance between ray and segment

        self.debug_plane_intersections = [False] * 3

        self.original_position = vec3(0)
        self.original_axes_p0 = [vec3(0)] * 3
        self.original_axes_p1 = [vec3(0)] * 3

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4):

        if self.gizmo_mode == constants.GIZMO_MODE_TRANSLATION:
            self.render_gizmo_translation_mode(
                view_matrix=view_matrix,
                projection_matrix=projection_matrix,
                model_matrix=model_matrix)

        if self.gizmo_mode == constants.GIZMO_MODE_ROTATION:
            pass

        if self.gizmo_mode == constants.GIZMO_MODE_SCALE:
            pass

    def render_gizmo_translation_mode(self,
                                      view_matrix: mat4,
                                      projection_matrix: mat4,
                                      model_matrix: mat4):

        # Calculate the camera position from the view matrix
        camera_position = inverse(view_matrix) * vec4(0.0, 0.0, 0.0, 1.0)
        camera_position = vec3(camera_position)  # Convert to vec3

        # Determine the scale factor to keep the gizmo a constant size on the screen
        gizmo_position = vec3(model_matrix[3])
        distance = length(camera_position - gizmo_position)
        self.gizmo_scale = distance * self.gizmo_size_on_screen

        # Update vertices with the new scale factor
        self.update_translation_vertices(self.gizmo_scale)

        # No need to apply the scale to the entity matrix
        transform_matrix = projection_matrix * view_matrix * model_matrix

        # Bind the helper framebuffer to clear the depth buffer
        self.helper_fbo.use()
        self.helper_fbo.clear(depth=True)

        # Bind the output framebuffer to render the gizmo
        self.output_fbo.use()

        # Pass the transform matrix to the shader
        self.program['uViewProjMatrix'].write(transform_matrix)

        # Pass the viewport size to the geometry shader
        viewport_size = (self.output_fbo.viewport[2], self.output_fbo.viewport[3])
        self.program['uViewport'].value = viewport_size

        # Set the line width
        self.ctx.line_width = 3.0

        # Render the gizmo axes
        self.translation_vao.render(moderngl.LINES)

    def generate_translation_vertices(self):

        # Create buffer and vertex array for the gizmo
        self.translation_vbo = self.ctx.buffer(constants.GIZMO_TRANSLATION_VERTICES.tobytes())
        self.translation_vao = self.ctx.simple_vertex_array(self.program,
                                                            self.translation_vbo,
                                                            'aPositionSize',
                                                            'aColor')

    def update_translation_vertices(self, scale_factor):

        # TODO: [performance] Re-creating arrays here!
        scale_vector = np.array([scale_factor, scale_factor, scale_factor, 1.0, 1.0, 1.0, 1.0, 1.0], dtype='f4').reshape(1, -1)
        scaled_vertices = constants.GIZMO_TRANSLATION_VERTICES * scale_vector

        # Update the VBO with the new vertices
        self.translation_vbo.write(scaled_vertices.tobytes())

    # =========================================================================
    #                           Input Callbacks
    # =========================================================================

    def handle_event_mouse_button_press(self, button: int, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4):

        a = button == constants.MOUSE_LEFT
        b = self.state == constants.GIZMO_STATE_HOVERING_AXES or self.state == constants.GIZMO_STATE_HOVERING_PLANES
        if a and b:

            self.original_position = vec3(model_matrix[3])

            # Update axis long segments so that we can start dragging the gizmo along
            tr_axis_p0_list = []
            tr_axis_p1_list = []
            for axis_index in range(len(self.original_axes_p0)):
                axis_direction = vec3(model_matrix[axis_index])
                tr_axis_p0_list.append(self.original_position - constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
                tr_axis_p1_list.append(self.original_position + constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
            self.original_axes_p0 = tr_axis_p0_list
            self.original_axes_p1 = tr_axis_p1_list

            # Get offset on axis where you first clicked, the "translation offset"
            self.gizmo_translation_offset_point, _ = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=self.original_axes_p0[self.active_axis_index],
                p1=self.original_axes_p1[self.active_axis_index]
            )
            self.gizmo_translation_offset_point -= self.original_position
            self.state = constants.GIZMO_STATE_DRAGGING_AXIS

    def handle_event_mouse_button_release(self, button: int, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4):
        if button == constants.MOUSE_LEFT:
            self.state = constants.GIZMO_STATE_INACTIVE

    def handle_event_keyboard_press(self, event_data: tuple) -> mat4:
        key, modifiers = event_data
        # Add code here as needed
        return None

    def handle_event_keyboard_release(self, event_data: tuple)-> mat4:
        key, modifiers = event_data
        # Add code here as needed
        return None

    def handle_event_mouse_move(self, event_data: tuple, ray_origin: vec3, ray_direction: vec3,
                                model_matrix: mat4) -> mat4:
        x, y, dx, dy = event_data

        if model_matrix is None:
            return None

        is_hovering_axes = False
        is_hovering_patches = False

        # ================[ Resolve Axes ]==================

        # Calculate distances between ray and axes
        gizmo_position = vec3(model_matrix[3])
        self.ray_to_axis_dist2 = [math_3d.distance2_ray_segment(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            p0=gizmo_position,
            p1=vec3(model_matrix[i]) * self.gizmo_scale + gizmo_position) for i in range(3)]

        shortest_axis_dist_index = np.argmin(self.ray_to_axis_dist2)
        shortest_axis_distance = self.ray_to_axis_dist2[shortest_axis_dist_index]

        if shortest_axis_distance < self.gizmo_scale * constants.GIZMO_AXIS_DETECTION_RADIUS:
            is_hovering_axes = True
            self.active_axis_index = shortest_axis_dist_index
        else:
            is_hovering_axes = False
            self.active_axis_index = -1

        # ================[ Resolve Planes ]==================

        # Detect if any of the 3 planes are being intersected
        a = constants.GIZMO_PLANE_OFFSET * self.gizmo_scale
        b = a + constants.GIZMO_PLANE_SIZE * self.gizmo_scale

        plane_intersections = []

        for index, axis_indices in enumerate(self.plane_axis_list):

            u, v, t = math_3d.ray_intersect_plane_coordinates(
                plane_origin=gizmo_position,
                plane_vec1=vec3(model_matrix[axis_indices[0]]) * self.gizmo_scale,
                plane_vec2=vec3(model_matrix[axis_indices[1]]) * self.gizmo_scale,
                ray_origin=ray_origin,
                ray_direction=ray_direction
            )

            # ray does not hit infinite plane
            if t is None:
                continue

            # Check if ray hits small patch on the plane
            if u is not None and a <= u <= b and a <= v <= b:
                plane_intersections.append((index, u, v, t))

        # Resolve which patch is the closest
        if len(plane_intersections) > 0:
            is_hovering_patches = True
            closest_plane_patch = min(plane_intersections, key=lambda x: x[3])  # x[3] is the t value
            self.active_plane_index = closest_plane_patch[0]
            closest_plane_distance = closest_plane_patch[3]
        else:
            is_hovering_patches = False
            self.active_plane_index = -1
            closest_plane_distance = float('inf')

        if is_hovering_axes and not is_hovering_patches:
            self.state = constants.GIZMO_STATE_HOVERING_AXES
        elif not is_hovering_axes and is_hovering_patches:
            self.state = constants.GIZMO_STATE_HOVERING_PLANES
        else:
            # Resolve disambiguation between axes and patches
            pass

        self.debug_plane_intersections = [plane[0] for plane in plane_intersections]

        return None

    def handle_event_mouse_drag(self, event_data: tuple, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> mat4:
        x, y, dx, dy = event_data

        if model_matrix is None:
            return None

        if self.active_axis_index == -1:
            return None

        # TODO: Ignore this function if the right button is being dragged!

        if self.state == constants.GIZMO_STATE_DRAGGING_AXIS:

            # Mark the projected point
            current_position = vec3(model_matrix[3])
            axis_direction = vec3(model_matrix[self.active_axis_index])

            nearest_point_on_axis, _ = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=self.original_axes_p0[self.active_axis_index],
                p1=self.original_axes_p1[self.active_axis_index],
            )

            delta_vector = nearest_point_on_axis - current_position - self.gizmo_translation_offset_point
            return translate(model_matrix, delta_vector)