import math
import moderngl
import numpy as np

import imgui
from typing import Any
from glm import vec3, vec4, mat4, length, length2, inverse, translate, rotate, scale, dot, normalize, sin, cos, cross
import copy

from src3 import constants
from src3 import math_3d
from src3.gizmos import gizmo_constants
from src3.gizmos import gizmo_utils
from src3.gizmos.gizmo import Gizmo
from src3.mesh_factory_3d import MeshFactory3D


class TransformGizmo(Gizmo):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.alpha = 0.75
        self.scale = 1.0
        self.mode = gizmo_constants.GIZMO_MODE_TRANSLATION
        self.state = gizmo_constants.GIZMO_STATE_INACTIVE
        self.active_index = -1  # Axis or plane
        self.previous_state_and_index = (self.state, self.active_index)  # Used to minimise vbo updates

        # Dynamic offsets when gizmos are dragged
        self.axis_offset_point = vec3(0, 0, 0)
        self.plane_offset_point = vec3(0, 0, 0)
        self.center_offset_point = vec3(0, 0, 0)
        self.disk_offset_angle = 0.0

        self.ray_to_axis_dist2 = [0.0] * 3  # Closest distance between ray and segment
        self.update_colors = np.ndarray((30, 4), dtype='f4')
        self.plane_axis_list = [(0, 1), (0, 2), (1, 2)]
        self.disks_axis_list = [(1, 2), (0, 2), (0, 1)]

        # VAOs and VBOs
        self.translation_mode_lines_vbos = {}
        self.translation_mode_lines_vaos = {}
        self.translation_mode_lines_vertices_vbo = None
        self.translation_mode_lines_colors_vbo = None
        self.translation_mode_lines_vao = None
        self.translation_mode_triangles_vbo = None
        self.translation_mode_triangles_vao = None

        self.rotation_mode_lines_vbos = {}  # All 3 axes
        self.rotation_mode_lines_vaos = {}

        self.axis_guide_vbo = None
        self.axis_guide_vao = None
        self.center_triangles_vbo = None
        self.center_triangles_vao = None
        self.center_triangles_highlight_vbo = None
        self.center_triangles_highlight_vao = None

        self.generate_translation_mode_vbos_and_vaos()
        self.generate_rotation_mode_vbos_and_vaos()

        self.original_model_matrix = mat4(1.0)
        self.original_position = vec3(0.0)
        self.original_axes_p0 = [vec3(0)] * 3
        self.original_axes_p1 = [vec3(0)] * 3
        self.original_rotation_angle = 0.0

        self.debug_plane_intersections = []
        self.debug_rotation_delta = 0.0
        self.debug_intersection_u = 0.0
        self.debug_intersection_v = 0.0

    def set_mode_translation(self):
        self.gizmo_size_on_screen_pixels = gizmo_constants.GIZMO_SIZE_ON_SCREEN_PIXELS_TRANSLATION
        self.mode = gizmo_constants.GIZMO_MODE_TRANSLATION

    def set_mode_rotation(self):
        self.gizmo_size_on_screen_pixels = gizmo_constants.GIZMO_SIZE_ON_SCREEN_PIXELS_ROTATION
        self.mode = gizmo_constants.GIZMO_MODE_ROTATION

    def set_orientation_global(self):
        self.orientation = gizmo_constants.GIZMO_ORIENTATION_GLOBAL

    def set_orientation_local(self):
        self.orientation = gizmo_constants.GIZMO_ORIENTATION_LOCAL

    def set_viewport(self, viewport: tuple):
        self.original_viewport = viewport

    def render(self,
               view_matrix: mat4,
               projection_matrix: mat4,
               model_matrix: mat4,
               component: Any):

        """
        The render function of the transform gizmo is different from other gizmos as it can render with only
        a model matrix.
        :param view_matrix:
        :param projection_matrix:
        :param model_matrix:
        :param component:
        :return:
        """

        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND)

        # Calculate the camera position from the view matrix
        camera_position = inverse(view_matrix) * vec4(0.0, 0.0, 0.0, 1.0)
        camera_position = vec3(camera_position)  # Convert to vec3

        # Apply the scale to the model matrix
        scaled_model_matrix = self.calculate_scaled_model_matrix(camera_position=camera_position,
                                                                 projection_matrix=projection_matrix,
                                                                 model_matrix=model_matrix)

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
        self.ctx.line_width = 3.0  # TODO: Figure out how this affects the line rendering

        # Important! Run this before you render to make sure your vbos are reflecting the current state!
        self.trigger_vbo_state_update()

        rendering_state = (self.state, self.active_index)

        if self.mode == gizmo_constants.GIZMO_MODE_TRANSLATION:

            # TODO: Resolve Z-fighting here by rendering the axis guide and clearing the depth buffer once more (?)
            self.translation_mode_lines_vao.render(moderngl.LINES)

            self.program_triangles['uViewProjMatrix'].write(transform_matrix)

            # Centers
            if self.state in (gizmo_constants.GIZMO_STATE_HOVERING_CENTER, gizmo_constants.GIZMO_STATE_DRAGGING_CENTER):
                self.center_triangles_highlight_vao.render(moderngl.TRIANGLES)
            else:
                self.center_triangles_vao.render(moderngl.TRIANGLES)

            # Axis Guides
            if self.state == gizmo_constants.GIZMO_STATE_DRAGGING_AXIS:
                world_transform_matrix = projection_matrix * view_matrix * mat4(1.0)
                self.program_lines['uViewProjMatrix'].write(world_transform_matrix)
                self.axis_guide_vao.render(moderngl.LINES)

        if self.mode == gizmo_constants.GIZMO_MODE_ROTATION:
            if rendering_state in self.rotation_mode_lines_vaos:
                self.rotation_mode_lines_vaos[rendering_state].render(moderngl.LINES)

        if self.mode == gizmo_constants.GIZMO_MODE_SCALE:
            pass


    def trigger_vbo_state_update(self):

        # TODO: Think if there is an easier way to pre-allocate all this memory

        current_state_and_index = (self.state, self.active_index)
        if current_state_and_index == self.previous_state_and_index:
            # If there was no change in state or axis, then there is nothing to update
            return

        # Reset colors
        num_vertices = gizmo_constants.GIZMO_MODE_TRANSLATION_DEFAULT_COLORS.shape[0]
        self.update_colors[:] = np.concatenate([gizmo_constants.GIZMO_MODE_TRANSLATION_DEFAULT_COLORS,
                                                np.ones((num_vertices, 1), dtype='f4') * self.alpha], axis=1)

        # Update only the colors pertaining to the current state and active axis, IF it is valid
        if current_state_and_index in gizmo_constants.GIZMO_MODE_TRANSLATION_RANGES:
            (a, b) = gizmo_constants.GIZMO_MODE_TRANSLATION_RANGES[current_state_and_index]
            self.update_colors[a:b, :] = np.array(gizmo_constants.GIZMO_HIGHLIGHT + [self.alpha], dtype='f4')

        self.translation_mode_lines_colors_vbo.write(self.update_colors.tobytes())

        # And finally update our previous state
        self.previous_state_and_index = current_state_and_index

    # =========================================================================
    #                           Input Callbacks
    # =========================================================================

    def handle_event_mouse_button_press(self,
                                        event_data: tuple,
                                        ray_origin: vec3,
                                        ray_direction: vec3,
                                        model_matrix: mat4,
                                        component: Any):

        if self.mode == gizmo_constants.GIZMO_MODE_TRANSLATION:
            self.translation_mode_mouse_press(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

        elif self.mode == gizmo_constants.GIZMO_MODE_ROTATION:
            self.rotation_mode_mouse_press(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

    def handle_event_mouse_button_release(self,
                                          event_data: tuple,
                                          ray_origin: vec3,
                                          ray_direction: vec3,
                                          model_matrix: mat4,
                                          component: Any):

        button, x, y = event_data

        # TODO: When you release the button, you need to check if tou are still hovering the gizmo
        if button == constants.MOUSE_LEFT:
            self.state = gizmo_constants.GIZMO_STATE_INACTIVE

    def handle_event_mouse_move(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any):
        x, y, dx, dy = event_data

        if model_matrix is None:
            return

        if self.mode == gizmo_constants.GIZMO_MODE_TRANSLATION:
            self.translation_mode_mouse_move(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

        if self.mode == gizmo_constants.GIZMO_MODE_ROTATION:
            self.rotation_mode_mouse_move(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

    def handle_event_mouse_drag(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:
        x, y, dx, dy = event_data

        if model_matrix is None:
            return None

        # TODO: Ignore this function if the right button is being dragged!
        if self.mode == gizmo_constants.GIZMO_MODE_TRANSLATION:
            return self.translation_mode_mouse_drag(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

        if self.mode == gizmo_constants.GIZMO_MODE_ROTATION:
            return self.rotation_mode_mouse_drag(
                event_data=event_data,
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                model_matrix=model_matrix,
                component=component)

    def release(self):

        # Release VAOs first
        if self.translation_mode_lines_vao:
            self.translation_mode_lines_vao.release()

        if self.translation_mode_triangles_vao:
            self.translation_mode_triangles_vao.release()

        # Then the VBOs
        if self.translation_mode_lines_vertices_vbo:
            self.translation_mode_lines_vertices_vbo.release()

        if self.translation_mode_triangles_vbo:
            self.translation_mode_triangles_vbo.release()

    # =============================================================
    #                   VAO and VBO creation functions
    # =============================================================

    def generate_translation_mode_vbos_and_vaos(self):

        # Release any previous vaos and vbos if any
        self.release()

        # Lines Vertices and Colors
        num_vertices = gizmo_constants.GIZMO_MODE_TRANSLATION_VERTICES.shape[0]
        self.translation_mode_lines_vertices_vbo = self.ctx.buffer(gizmo_constants.GIZMO_MODE_TRANSLATION_VERTICES.tobytes())
        colors = np.concatenate([gizmo_constants.GIZMO_MODE_TRANSLATION_DEFAULT_COLORS,
                                 np.ones((num_vertices, 1), dtype='f4') * self.alpha], axis=1)
        self.translation_mode_lines_colors_vbo = self.ctx.buffer(colors.tobytes(), dynamic=True)
        self.translation_mode_lines_vao = self.ctx.vertex_array(
            self.program_lines,
            [
                (self.translation_mode_lines_vertices_vbo, '4f', 'aPositionSize'),
                (self.translation_mode_lines_colors_vbo, '4f', 'aColor'),
            ]
        )

        # Generate guides for when the object is being moved along the axes
        self.axis_guide_vbo = self.ctx.buffer(gizmo_constants.GIZMO_TRANSLATION_VERTICES_AXIS_GUIDE.tobytes())
        self.axis_guide_vao = self.ctx.vertex_array(
            self.program_lines,
            [
                (self.axis_guide_vbo, '4f 4f', 'aPositionSize', 'aColor')
            ]
        )

        # Center
        center_data = self.generate_center_vertex_data(
            radius=gizmo_constants.GIZMO_CENTER_RADIUS,
            color=(0.7, 0.7, 0.7, self.alpha))
        self.center_triangles_vbo = self.ctx.buffer(center_data.tobytes())
        self.center_triangles_vao = self.ctx.vertex_array(
            self.program_triangles,
            [
                (self.center_triangles_vbo, '3f 4f', 'aPosition', 'aColor')
            ]
        )
        center_data = self.generate_center_vertex_data(
            radius=gizmo_constants.GIZMO_CENTER_RADIUS,
            color=(0.8, 0.8, 0.0, self.alpha))
        self.center_triangles_highlight_vbo = self.ctx.buffer(center_data.tobytes())
        self.center_triangles_highlight_vao = self.ctx.vertex_array(
            self.program_triangles,
            [
                (self.center_triangles_highlight_vbo, '3f 4f', 'aPosition', 'aColor')
            ]
        )

    def generate_rotation_mode_vbos_and_vaos(self):

        x_axis_normal = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(1.0, 0, 0, self.alpha),
            direction=vec3(1.0, 0, 0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )
        x_axis_highlight = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(*gizmo_constants.GIZMO_HIGHLIGHT, self.alpha),
            direction=vec3(1.0, 0, 0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )
        y_axis_normal = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(0, 1.0, 0, self.alpha),
            direction=vec3(0, 1.0, 0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )
        y_axis_highlight = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(*gizmo_constants.GIZMO_HIGHLIGHT, self.alpha),
            direction=vec3(0, 1.0, 0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )
        z_axis_normal = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(*gizmo_constants.GIZMO_DISK_Z_COLOR_NORMAL, self.alpha),
            direction=vec3(0, 0, 1.0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )
        z_axis_highlight = gizmo_utils.generate_disk_vertex_data(
            origin=vec3(0, 0, 0),
            line_width=5.0,
            color=(*gizmo_constants.GIZMO_HIGHLIGHT, self.alpha),
            direction=vec3(0, 0, 1.0),
            num_segments=gizmo_constants.GIZMO_DISK_NUM_SEGMENTS,
            radius=1.0
        )

        vertices_inactive = np.concatenate([x_axis_normal, y_axis_normal, z_axis_normal], axis=0)
        vertices_x_hovering = np.concatenate([x_axis_highlight, y_axis_normal, z_axis_normal], axis=0)
        vertices_y_hovering = np.concatenate([x_axis_normal, y_axis_highlight, z_axis_normal], axis=0)
        vertices_z_hovering = np.concatenate([x_axis_normal, y_axis_normal, z_axis_highlight], axis=0)

        # Create VBOs
        vbo_inactive = self.ctx.buffer(vertices_inactive.tobytes())
        vbo_x_hovering = self.ctx.buffer(vertices_x_hovering.tobytes())
        vbo_y_hovering = self.ctx.buffer(vertices_y_hovering.tobytes())
        vbo_z_hovering = self.ctx.buffer(vertices_z_hovering.tobytes())

        vbo_dragging_x = self.ctx.buffer(x_axis_highlight.tobytes())
        vbo_dragging_y = self.ctx.buffer(y_axis_highlight.tobytes())
        vbo_dragging_z = self.ctx.buffer(z_axis_highlight.tobytes())

        self.rotation_mode_lines_vbos = {
            (gizmo_constants.GIZMO_STATE_INACTIVE, -1): vbo_inactive,
            (gizmo_constants.GIZMO_STATE_INACTIVE, 0): vbo_inactive,
            (gizmo_constants.GIZMO_STATE_INACTIVE, 1): vbo_inactive,
            (gizmo_constants.GIZMO_STATE_INACTIVE, 2): vbo_inactive,
            (gizmo_constants.GIZMO_STATE_HOVERING_DISK, 0): vbo_x_hovering,
            (gizmo_constants.GIZMO_STATE_HOVERING_DISK, 1): vbo_y_hovering,
            (gizmo_constants.GIZMO_STATE_HOVERING_DISK, 2): vbo_z_hovering,
            (gizmo_constants.GIZMO_STATE_DRAGGING_DISK, 0): vbo_dragging_x,
            (gizmo_constants.GIZMO_STATE_DRAGGING_DISK, 1): vbo_dragging_y,
            (gizmo_constants.GIZMO_STATE_DRAGGING_DISK, 2): vbo_dragging_z,
        }

        # Create VAOs
        for state_condition, selected_vbo in self.rotation_mode_lines_vbos.items():
            self.rotation_mode_lines_vaos[state_condition] = self.ctx.vertex_array(
                self.program_lines,
                [
                    (selected_vbo, '4f 4f', 'aPositionSize', 'aColor'),
                ]
            )

    # =============================================================
    #                Translation Mode-Specific Functions
    # =============================================================

    def translation_mode_mouse_press(self,
                                     event_data: tuple,
                                     ray_origin: vec3,
                                     ray_direction: vec3,
                                     model_matrix: mat4,
                                     component: Any):

        button, x, y = event_data

        if button == constants.MOUSE_LEFT:

            if self.state in [gizmo_constants.GIZMO_STATE_HOVERING_AXIS, gizmo_constants.GIZMO_STATE_HOVERING_PLANE]:

                self.update_original_model_matrx(model_matrix=model_matrix)

            if self.state == gizmo_constants.GIZMO_STATE_HOVERING_AXIS:

                # Get offset on axis where you first clicked, the "translation offset"
                self.axis_offset_point, _ = math_3d.nearest_point_on_segment(
                    ray_origin=ray_origin,
                    ray_direction=ray_direction,
                    p0=self.original_axes_p0[self.active_index],
                    p1=self.original_axes_p1[self.active_index]
                )
                self.axis_offset_point -= self.original_position
                self.state = gizmo_constants.GIZMO_STATE_DRAGGING_AXIS

                # Update data on the Axis guide to highlight which axis is being dragged
                if self.axis_guide_vbo:
                    p0 = self.original_axes_p0[self.active_index]
                    p1 = self.original_axes_p1[self.active_index]
                    new_data = np.array(
                        [  # These values are placeholders. They are overwritten dynamically
                            [p0.x, p0.y, p0.z, gizmo_constants.GIZMO_AXIS_GUIDE_LINE_WIDTH, 0.0, 0.0, 0.0, 0.8],
                            [p1.x, p1.y, p1.z, gizmo_constants.GIZMO_AXIS_GUIDE_LINE_WIDTH, 0.0, 0.0, 0.0, 0.8]
                        ],
                        dtype='f4'
                    )

                    # Set colour corresponding to the axis
                    new_data[:, 4 + self.active_index] = 1.0
                    self.axis_guide_vbo.write(new_data.tobytes())

                return

            if self.state == gizmo_constants.GIZMO_STATE_HOVERING_PLANE:

                plane_axis_indices = self.plane_axis_list[self.active_index]
                u, v, t = math_3d.ray_intersect_plane_coordinates(
                    plane_origin=self.original_position,
                    plane_vec1=vec3(model_matrix[plane_axis_indices[0]]) * self.scale,
                    plane_vec2=vec3(model_matrix[plane_axis_indices[1]]) * self.scale,
                    ray_origin=ray_origin,
                    ray_direction=ray_direction
                )
                self.plane_offset_point = ray_origin + ray_direction * t
                self.plane_offset_point -= self.original_position
                self.state = gizmo_constants.GIZMO_STATE_DRAGGING_PLANE
                return

            if self.state == gizmo_constants.GIZMO_STATE_HOVERING_CENTER:
                # Calculate the plane normal (same as the ray direction)
                plane_normal = normalize(ray_direction)

                # Calculate the plane offset
                plane_offset = dot(plane_normal, self.original_position)

                # Calculate the intersection of the ray with the plane
                is_intersecting, t = math_3d.intersect_ray_plane(
                    ray_origin=ray_origin,
                    ray_direction=ray_direction,
                    plane_normal=plane_normal,
                    plane_offset=plane_offset
                )
                if is_intersecting:
                    self.center_offset_point = ray_origin + ray_direction * t
                    self.center_offset_point -= self.original_position
                    self.state = gizmo_constants.GIZMO_STATE_DRAGGING_CENTER

                return

    def translation_mode_mouse_move(self,
                                    event_data: tuple,
                                    ray_origin: vec3,
                                    ray_direction: vec3,
                                    model_matrix: mat4,
                                    component: Any):
        x, y, dx, dy = event_data

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
        closest_state = gizmo_constants.GIZMO_STATE_INACTIVE
        closest_index = -1

        # Determine the closest interaction
        if is_hovering_center and center_t < closest_t:
            closest_t = center_t
            closest_state = gizmo_constants.GIZMO_STATE_HOVERING_CENTER
            closest_index = -1  # No active index for center

        if is_hovering_axis and axis_t < closest_t:
            closest_t = axis_t
            closest_state = gizmo_constants.GIZMO_STATE_HOVERING_AXIS
            closest_index = active_axis_index

        if is_hovering_plane and plane_t < closest_t:
            closest_state = gizmo_constants.GIZMO_STATE_HOVERING_PLANE
            closest_index = active_plane_index

        # Update state and active index
        self.state = closest_state
        self.active_index = closest_index

    def translation_mode_mouse_drag(self,
                                    event_data: tuple,
                                    ray_origin: vec3,
                                    ray_direction: vec3,
                                    model_matrix: mat4,
                                    component: Any) -> mat4:
        x, y, dx, dy = event_data

        # TODO: Ignore this function if the right button is being dragged!
        if self.state == gizmo_constants.GIZMO_STATE_DRAGGING_CENTER:

            # Calculate the plane normal (same as the ray direction)
            plane_normal = normalize(ray_direction)

            # Calculate the plane origin (gizmo position)
            plane_origin = vec3(model_matrix[3])

            # Calculate the intersection of the ray with the plane
            is_intersecting, t = math_3d.intersect_ray_plane(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                plane_normal=plane_normal,
                plane_offset=dot(plane_normal, plane_origin)
            )

            if not is_intersecting:
                return None

            # Calculate the new position on the plane
            new_plane_point = ray_origin + ray_direction * t

            # Calculate the delta movement based on the new plane point
            delta_vector = new_plane_point - self.original_position

            # Create a new translation matrix
            new_model_matrix = mat4(self.original_model_matrix)
            new_model_matrix[3] = vec4(delta_vector + self.original_position, 1.0)

            return new_model_matrix

        if self.state == gizmo_constants.GIZMO_STATE_DRAGGING_AXIS and self.active_index > -1:

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

        if self.state == gizmo_constants.GIZMO_STATE_DRAGGING_PLANE and self.active_index > -1:

            # Calculate the plane origin and direction vectors
            plane_axis_indices = self.plane_axis_list[self.active_index]
            plane_origin = self.original_position
            plane_vec1 = vec3(self.original_model_matrix[plane_axis_indices[0]])
            plane_vec2 = vec3(self.original_model_matrix[plane_axis_indices[1]])

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
            delta_vector = new_plane_point - self.plane_offset_point

            # Create a new translation matrix
            new_model_matrix = mat4(self.original_model_matrix)
            new_model_matrix[3] = vec4(delta_vector, 1.0)

            return new_model_matrix

    # =============================================================
    #                Rotation Mode-Specific Functions
    # =============================================================

    def calculate_rotation_angle(self,
                                 ray_origin: vec3,
                                 ray_direction: vec3,
                                 active_index: int) -> float:

        plane_vec1 = vec3(self.original_model_matrix[self.plane_axis_list[active_index][0]])
        plane_vec2 = vec3(self.original_model_matrix[self.plane_axis_list[active_index][1]])

        u, v, t = math_3d.ray_intersect_plane_coordinates(
            plane_origin=self.original_position,
            plane_vec1=plane_vec1,
            plane_vec2=plane_vec2,
            ray_origin=ray_origin,
            ray_direction=ray_direction
        )

        if t is not None:
            intersection_point = ray_origin + t * ray_direction
            vector_to_point = intersection_point - self.original_position
            rotation_angle = math.atan2(dot(vector_to_point, plane_vec2), dot(vector_to_point, plane_vec1))
            return rotation_angle

        return 0.0

    def rotation_mode_mouse_press(self,
                                  event_data: tuple,
                                  ray_origin: vec3,
                                  ray_direction: vec3,
                                  model_matrix: mat4,
                                  component: Any):

        if self.state in [gizmo_constants.GIZMO_STATE_HOVERING_DISK, gizmo_constants.GIZMO_STATE_DRAGGING_DISK]:
            self.update_original_model_matrx(model_matrix=model_matrix)

        if self.state == gizmo_constants.GIZMO_STATE_HOVERING_DISK:

            # Determine initial angle of rotation based on the ray's closest project point to the circumference
            self.original_rotation_angle = self.calculate_rotation_angle(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                active_index=self.active_index)

            self.state = gizmo_constants.GIZMO_STATE_DRAGGING_DISK

    def rotation_mode_mouse_move(self,
                                    event_data: tuple,
                                    ray_origin: vec3,
                                    ray_direction: vec3,
                                    model_matrix: mat4,
                                    component: Any):
        x, y, dx, dy = event_data

        # Initialize the closest state and distance
        closest_t = float('inf')
        self.state = gizmo_constants.GIZMO_STATE_INACTIVE
        self.active_index = -1

        is_hovering_disk, center_t, active_index = self.check_disk_hovering(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            model_matrix=model_matrix)

        if is_hovering_disk:
            self.state = gizmo_constants.GIZMO_STATE_HOVERING_DISK
            self.active_index = active_index

    def calculate_angle_delta(self, original_angle: float, current_angle: float) -> float:
        delta_angle = current_angle - original_angle
        while delta_angle > math.pi:
            delta_angle -= 2 * math.pi
        while delta_angle < -math.pi:
            delta_angle += 2 * math.pi
        return delta_angle

    def rotation_mode_mouse_drag(self,
                                 event_data: tuple,
                                 ray_origin: vec3,
                                 ray_direction: vec3,
                                 model_matrix: mat4,
                                 component: Any) -> mat4:

        if self.state == gizmo_constants.GIZMO_STATE_DRAGGING_DISK and self.active_index > -1:

            current_rotation_angle = self.calculate_rotation_angle(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                active_index=self.active_index)

            if current_rotation_angle is not None:
                rotation_delta = self.calculate_angle_delta(self.original_rotation_angle, current_rotation_angle)
                self.debug_rotation_delta = rotation_delta

                plane_vec1 = vec3(self.original_model_matrix[self.disks_axis_list[self.active_index][0]])
                plane_vec2 = vec3(self.original_model_matrix[self.disks_axis_list[self.active_index][1]])
                rotation_axis = normalize(cross(plane_vec1, plane_vec2))
                rotation_matrix = rotate(mat4(1.0), rotation_delta, rotation_axis)

                # Extract the translation from the original model matrix
                translation = vec3(self.original_model_matrix[3])

                # Apply the rotation to the original model matrix without translation
                original_model_matrix_no_translation = mat4(self.original_model_matrix)
                original_model_matrix_no_translation[3] = vec4(0.0, 0.0, 0.0, 1.0)

                # Apply rotation
                new_model_matrix = rotation_matrix * original_model_matrix_no_translation

                # Reapply the translation
                new_model_matrix[3] = vec4(translation, 1.0)

                return new_model_matrix

        return None

    # =============================================================
    #                Hovering-check functions
    # =============================================================

    def check_disk_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:

        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')
        active_index = -1

        plane_intersections = []
        for index, axis_indices in enumerate(self.disks_axis_list):

            # t is distance to camera
            u, v, t = math_3d.ray_intersect_plane_coordinates(
                plane_origin=gizmo_position,
                plane_vec1=vec3(model_matrix[axis_indices[0]]),
                plane_vec2=vec3(model_matrix[axis_indices[1]]),
                ray_origin=ray_origin,
                ray_direction=ray_direction
            )

            # ray does not hit infinite plane
            if t is None:
                continue

            # Calculate the intersection point
            intersection_point = ray_origin + t * ray_direction
            dist_to_center = length(intersection_point - gizmo_position)

            # NOTE: We substract scale because the length of axis is always 1.0! The vectors from the model matrix are unitary!
            scaled_threshold = gizmo_constants.GIZMO_DISK_EDGE_THICKNESS * self.scale
            delta = dist_to_center - self.scale
            if -scaled_threshold <= delta <= scaled_threshold:
                plane_intersections.append((index, delta, t))

        self.debug_plane_intersections = "\n".join([str(inter) for inter in plane_intersections])

        if len(plane_intersections) > 0:
            closest_plane_patch = min(plane_intersections, key=lambda x: x[1])  # x[1] is distance to the edge
            active_index = closest_plane_patch[0]
            ray_t = closest_plane_patch[2]
            is_hovering = True

        return is_hovering, ray_t, active_index

    def check_center_hovering(self,
                              ray_origin: vec3,
                              ray_direction: vec3,
                              model_matrix: mat4) -> tuple:
        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')

        center_dist2 = math_3d.distance2_ray_point(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            point=gizmo_position
        )

        if center_dist2 < (self.scale * gizmo_constants.GIZMO_CENTER_RADIUS) ** 2:

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
            p0=gizmo_position + vec3(model_matrix[i]) * gizmo_constants.GIZMO_AXIS_OFFSET * self.scale,
            p1=gizmo_position + vec3(model_matrix[i]) * (
                        gizmo_constants.GIZMO_AXIS_OFFSET + gizmo_constants.GIZMO_AXIS_LENGTH) * self.scale)
            for i in range(3)]

        shortest_dist2_axis_index = np.argmin(self.ray_to_axis_dist2)
        shortest_dist2 = self.ray_to_axis_dist2[shortest_dist2_axis_index]

        if shortest_dist2 < self.scale ** 2 * gizmo_constants.GIZMO_AXIS_DETECTION_RADIUS_2:
            active_index = shortest_dist2_axis_index
            projected_point, ray_t = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=gizmo_position,
                p1=vec3(model_matrix[shortest_dist2_axis_index]) * self.scale + gizmo_position)

            is_hovering = True

        return is_hovering, ray_t, active_index

    def check_plane_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:

        gizmo_position = vec3(model_matrix[3])
        is_hovering = False
        ray_t = float('inf')
        active_index = -1

        # Detect if any of the 3 planes are being intersected
        a = gizmo_constants.GIZMO_PLANE_OFFSET * self.scale
        b = a + gizmo_constants.GIZMO_PLANE_SIZE * self.scale

        plane_intersections = []
        for index, axis_indices in enumerate(self.plane_axis_list):

            u, v, t = math_3d.ray_intersect_plane_coordinates(
                plane_origin=gizmo_position,
                plane_vec1=vec3(model_matrix[axis_indices[0]]),
                plane_vec2=vec3(model_matrix[axis_indices[1]]),
                ray_origin=ray_origin,
                ray_direction=ray_direction
            )

            # ray does not hit infinite plane
            if t is None:
                continue

            # Check if ray hits small patch on the plane
            if u is not None and a <= u <= b and a <= v <= b:
                plane_intersections.append((index, u, v, t))

        # Resolve which plane patch is the closest
        if len(plane_intersections) > 0:
            closest_plane_patch = min(plane_intersections, key=lambda x: x[3])  # x[3] is the t value
            active_index = closest_plane_patch[0]
            ray_t = closest_plane_patch[3]
            is_hovering = True

        return is_hovering, ray_t, active_index

    # =============================================================
    #                   Utility functions
    # =============================================================

    def update_original_model_matrx(self, model_matrix: mat4):
        """
        This function updates the gizmo's internal copy of the model matrix that is made when you
        activate a gizmo. This matrix is used to compar
        :param model_matrix:
        :return:
        """
        self.original_model_matrix = copy.deepcopy(model_matrix)
        self.original_position = vec3(self.original_model_matrix[3])

        # Update axis long segments so that we can start dragging the gizmo along
        tr_axis_p0_list = []
        tr_axis_p1_list = []
        for axis_index in range(len(self.original_axes_p0)):
            axis_direction = vec3(model_matrix[axis_index])
            tr_axis_p0_list.append(self.original_position - gizmo_constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
            tr_axis_p1_list.append(self.original_position + gizmo_constants.GIZMO_AXIS_SEGMENT_LENGTH * axis_direction)
        self.original_axes_p0 = tr_axis_p0_list
        self.original_axes_p1 = tr_axis_p1_list

    def generate_center_vertex_data(self, radius: float, color: tuple) -> np.ndarray:

        mesh_factory = MeshFactory3D()
        shape_list = [
            {"name": "icosphere",
             "radius": radius,
             "color": color,
             "subdivisions": 3},
        ]
        mesh_data = mesh_factory.generate_mesh(shape_list=shape_list)
        vertices_and_colors = np.concatenate([mesh_data["vertices"], mesh_data["colors"]], axis=1)

        return vertices_and_colors

    def render_ui(self):

        with imgui.begin_child("region", 250, 200, border=True):
            imgui.text(f"Transform Gizmo")
            imgui.separator()
            imgui.text(f"Mode: {self.mode}")
            imgui.text(f"State: {str(self.state)}")
            imgui.text(f"Axis: {self.active_index}")
            imgui.text(f"Scale: {self.scale}")