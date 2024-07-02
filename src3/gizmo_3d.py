import copy
import time

import moderngl
import numpy as np
from src3 import constants
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize

from src3 import math_3d
from src3.shader_loader import ShaderLoader


class Gizmo3D:

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

        self.translation_vbos = {}
        self.translation_vaos = {}
        self.generate_vaos()

        self.plane_axis_list = [(0, 1), (0, 2), (1, 2)]

        self.gizmo_scale = 1.0
        self.gizmo_mode = constants.GIZMO_MODE_TRANSLATION
        self.state = constants.GIZMO_STATE_INACTIVE
        self.active_index = -1  # Axis or plane
        self.axis_offset_point = vec3(0, 0, 0)
        self.plane_offset_point = vec3(0, 0, 0)
        self.ray_to_axis_dist2 = [0.0] * 3  # Closest distance between ray and segment

        self.debug_plane_intersections = [False] * 3

        self.original_model_matrix = mat4(1.0)
        self.original_position = vec3(0.0)
        self.original_axes_p0 = [vec3(0)] * 3
        self.original_axes_p1 = [vec3(0)] * 3

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4):

        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND)

        # Calculate the camera position from the view matrix
        camera_position = inverse(view_matrix) * vec4(0.0, 0.0, 0.0, 1.0)
        camera_position = vec3(camera_position)  # Convert to vec3

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
        scaled_model_matrix = model_matrix * scale_matrix

        # Create the final transform matrix
        transform_matrix = projection_matrix * view_matrix * scaled_model_matrix

        # Bind the helper framebuffer to clear the depth buffer
        self.helper_fbo.use()
        self.helper_fbo.clear(depth=True)

        # Bind the output framebuffer to render the gizmo
        self.output_fbo.use()

        # Pass the transform matrix to the shader
        self.program_lines['uViewProjMatrix'].write(transform_matrix)

        # Pass the viewport size to the geometry shader
        viewport_size = (self.output_fbo.viewport[2], self.output_fbo.viewport[3])
        self.program_lines['uViewport'].value = viewport_size

        # Set the line width
        self.ctx.line_width = 3.0

        if self.gizmo_mode == constants.GIZMO_MODE_TRANSLATION:
            try:
                self.translation_vaos[(self.state, self.active_index)].render(moderngl.LINES)
            except Exception as error:
                g = 0

            if self.state == constants.GIZMO_STATE_DRAGGING_AXIS:
                # Draw axis
                pass

        if self.gizmo_mode == constants.GIZMO_MODE_ROTATION:
            pass

        if self.gizmo_mode == constants.GIZMO_MODE_SCALE:
            pass

    def generate_vaos(self):

        # Release any previous vaos and vbos if any
        self.release()

        # First create VBOs for the hovering state
        self.translation_vbos = {}
        for state_name_and_active_index, vertices in constants.GIZMO_TRANSLATION_STATE_HOVERING_VERTEX_GROUP.items():
            self.translation_vbos[state_name_and_active_index] = self.ctx.buffer(vertices.tobytes())

        # Create one vao per vbo
        for _, vbo in self.translation_vaos:
            if vbo is not None:
                vbo.release()

        self.translation_vaos = {}
        for state_name_and_active_index, vbo in self.translation_vbos.items():
            self.translation_vaos[state_name_and_active_index] = self.ctx.simple_vertex_array(
                self.program_lines,
                vbo,
                'aPositionSize',
                'aColor')

    # =========================================================================
    #                           Input Callbacks
    # =========================================================================

    def handle_event_mouse_button_press(self, button: int, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4):

        if button == constants.MOUSE_LEFT:

            if self.state in [constants.GIZMO_STATE_HOVERING_AXIS, constants.GIZMO_STATE_HOVERING_PLANE]:

                self.original_model_matrix = copy.deepcopy(model_matrix)
                self.original_position = vec3(self.original_model_matrix[3])

                # Update axis long segments so that we can start dragging the gizmo along
                tr_axis_p0_list = []
                tr_axis_p1_list = []
                for axis_index in range(len(self.original_axes_p0)):
                    axis_direction = vec3(model_matrix[axis_index])
                    tr_axis_p0_list.append(self.original_position - constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
                    tr_axis_p1_list.append(self.original_position + constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
                self.original_axes_p0 = tr_axis_p0_list
                self.original_axes_p1 = tr_axis_p1_list

            if self.state == constants.GIZMO_STATE_HOVERING_AXIS:

                # Get offset on axis where you first clicked, the "translation offset"
                self.axis_offset_point, _ = math_3d.nearest_point_on_segment(
                    ray_origin=ray_origin,
                    ray_direction=ray_direction,
                    p0=self.original_axes_p0[self.active_index],
                    p1=self.original_axes_p1[self.active_index]
                )
                self.axis_offset_point -= self.original_position
                self.state = constants.GIZMO_STATE_DRAGGING_AXIS
                return

            if self.state == constants.GIZMO_STATE_HOVERING_PLANE:

                plane_axis_indices = self.plane_axis_list[self.active_index]
                u, v, t = math_3d.ray_intersect_plane_coordinates(
                    plane_origin=self.original_position,
                    plane_vec1=vec3(model_matrix[plane_axis_indices[0]]) * self.gizmo_scale,
                    plane_vec2=vec3(model_matrix[plane_axis_indices[1]]) * self.gizmo_scale,
                    ray_origin=ray_origin,
                    ray_direction=ray_direction
                )
                self.plane_offset_point = ray_origin + ray_direction * t
                self.state = constants.GIZMO_STATE_DRAGGING_PLANE
                return

    def handle_event_mouse_button_release(self, button: int, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4):

        # TODO: When you release the button, you need to check if tou are still hovering the gizmo
        if button == constants.MOUSE_LEFT:
            self.state = constants.GIZMO_STATE_INACTIVE

    def handle_event_keyboard_press(self, event_data: tuple) -> mat4:
        key, modifiers = event_data
        # Add code here as needed
        return None

    def handle_event_keyboard_release(self, event_data: tuple) -> mat4:
        key, modifiers = event_data
        # Add code here as needed
        return None

    def handle_event_mouse_move(self, event_data: tuple, ray_origin: vec3, ray_direction: vec3,
                                model_matrix: mat4) -> mat4:
        x, y, dx, dy = event_data

        if model_matrix is None:
            return None

        is_hovering_center, center_t = self.check_center_hovering(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            model_matrix=model_matrix)

        is_hovering_axis, axis_t, active_axis_index = self.check_axis_hovering(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            model_matrix=model_matrix)

        is_hovering_plane, plane_t, active_plane_index = self.check_plane_hovering(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            model_matrix=model_matrix)

        # Initialize the closest state and distance
        closest_t = float('inf')
        closest_state = constants.GIZMO_STATE_INACTIVE
        closest_index = -1

        # Determine the closest interaction
        if is_hovering_center and center_t < closest_t:
            closest_t = center_t
            closest_state = constants.GIZMO_STATE_HOVERING_CENTER
            closest_index = -1  # No active index for center

        if is_hovering_axis and axis_t < closest_t:
            closest_t = axis_t
            closest_state = constants.GIZMO_STATE_HOVERING_AXIS
            closest_index = active_axis_index

        if is_hovering_plane and plane_t < closest_t:
            closest_t = plane_t
            closest_state = constants.GIZMO_STATE_HOVERING_PLANE
            closest_index = active_plane_index

        # Update state and active index
        self.state = closest_state
        self.active_index = closest_index

        return None

    def handle_event_mouse_drag(self, event_data: tuple, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> mat4:
        x, y, dx, dy = event_data

        if model_matrix is None:
            return None

        if self.active_index == -1:
            return None

        # TODO: Ignore this function if the right button is being dragged!

        if self.state == constants.GIZMO_STATE_DRAGGING_AXIS:

            nearest_point_on_axis, _ = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=self.original_axes_p0[self.active_index],
                p1=self.original_axes_p1[self.active_index],
            )

            # Calculate the delta from the original position
            delta_vector = nearest_point_on_axis - self.axis_offset_point

            # Create a new translation matrix
            new_model_matrix = mat4(self.original_model_matrix)
            new_model_matrix[3] = vec4(delta_vector, 1.0)

            return new_model_matrix

        if self.state == constants.GIZMO_STATE_DRAGGING_PLANE:

            # Calculate the plane origin and direction vectors
            plane_axis_indices = self.plane_axis_list[self.active_index]
            plane_origin = self.original_position
            plane_vec1 = vec3(self.original_model_matrix[plane_axis_indices[0]]) * self.gizmo_scale
            plane_vec2 = vec3(self.original_model_matrix[plane_axis_indices[1]]) * self.gizmo_scale

            # Calculate intersection of ray with plane
            u, v, t = math_3d.ray_intersect_plane_coordinates(
                plane_origin=plane_origin,
                plane_vec1=plane_vec1,
                plane_vec2=plane_vec2,
                ray_origin=ray_origin,
                ray_direction=ray_direction
            )

            if t is None:
                return None

            # Calculate the new position on the plane
            new_plane_point = ray_origin + ray_direction * t

            # Calculate delta movement based on the new plane point
            delta_vector = new_plane_point - (self.plane_offset_point - self.original_position)

            # Create a new translation matrix
            new_model_matrix = mat4(self.original_model_matrix)
            new_model_matrix[3] = vec4(delta_vector, 1.0)

            return new_model_matrix

    def check_center_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:
        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')

        center_dist2 = math_3d.distance2_ray_point(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            point=gizmo_position
        )

        if center_dist2 < constants.GIZMO_CENTER_RADIUS_2:
            # Normalize the ray direction
            direction_normalized = normalize(ray_direction)
            # Calculate the vector from the ray origin to the gizmo position
            origin_to_gizmo = gizmo_position - ray_origin
            # Calculate ray_t as the dot product of origin_to_gizmo and the normalized direction
            ray_t = dot(origin_to_gizmo, direction_normalized)
            if ray_t >= 0.0:
                is_hovering = True

        return is_hovering, ray_t

    def check_axis_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:

        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')
        active_index = -1

        self.ray_to_axis_dist2 = [math_3d.distance2_ray_segment(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            p0=gizmo_position + vec3(model_matrix[i]) * constants.GIZMO_AXIS_OFFSET * self.gizmo_scale,
            p1=gizmo_position + vec3(model_matrix[i]) * (
                        constants.GIZMO_AXIS_OFFSET + constants.GIZMO_AXIS_LENGTH) * self.gizmo_scale)
            for i in range(3)]

        shortest_dist2_axis_index = np.argmin(self.ray_to_axis_dist2)
        shortest_dist2 = self.ray_to_axis_dist2[shortest_dist2_axis_index]

        if shortest_dist2 < self.gizmo_scale ** 2 * constants.GIZMO_AXIS_DETECTION_RADIUS_2:
            active_index = shortest_dist2_axis_index
            projected_point, ray_t = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=gizmo_position,
                p1=vec3(model_matrix[shortest_dist2_axis_index]) * self.gizmo_scale + gizmo_position)

            is_hovering = True

        return is_hovering, ray_t, active_index

    def check_plane_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:

        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')
        active_index = -1

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

        # DEBUG
        self.debug_plane_intersections = [plane[0] for plane in plane_intersections]

        # Resolve which plane patch is the closest
        if len(plane_intersections) > 0:
            closest_plane_patch = min(plane_intersections, key=lambda x: x[3])  # x[3] is the t value
            active_index = closest_plane_patch[0]
            ray_t = closest_plane_patch[3]
            is_hovering = True

        return is_hovering, ray_t, active_index

    def release(self):

        for _, vao in self.translation_vaos.items():
            if vao:
                vao.release()

        for _, vbo in self.translation_vbos.items():
            if vbo:
                vbo.release()



