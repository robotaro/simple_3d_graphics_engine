import moderngl
import numpy as np
from src3 import constants
import imgui
from typing import Any
from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize
import copy

from src3 import math_3d
from src3.gizmos.gizmo import Gizmo
from src3.shader_loader import ShaderLoader
from src3.mesh_factory_3d import MeshFactory3D


class TransformGizmo(Gizmo):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.helper_fbo = self.ctx.framebuffer(
            depth_attachment=self.output_fbo.depth_attachment,
        )

        self.translation_mode_lines_vbos = {}
        self.translation_mode_lines_vaos = {}
        self.axis_guide_vbo = None
        self.axis_guide_vao = None
        self.center_triangles_vbo = None
        self.center_triangles_vao = None
        self.center_triangles_highlight_vbo = None
        self.center_triangles_highlight_vao = None
        self.generate_vbos_and_vaos()

        self.plane_axis_list = [(0, 1), (0, 2), (1, 2)]

        self.gizmo_scale = 1.0
        self.gizmo_mode = constants.GIZMO_MODE_TRANSLATION
        self.state = constants.GIZMO_STATE_INACTIVE
        self.active_index = -1  # Axis or plane
        self.axis_offset_point = vec3(0, 0, 0)
        self.plane_offset_point = vec3(0, 0, 0)
        self.center_offset_point = vec3(0, 0, 0)
        self.ray_to_axis_dist2 = [0.0] * 3  # Closest distance between ray and segment

        self.original_model_matrix = mat4(1.0)
        self.original_position = vec3(0.0)
        self.original_axes_p0 = [vec3(0)] * 3
        self.original_axes_p1 = [vec3(0)] * 3

    def generate_vbos_and_vaos(self):

        # Release any previous vaos and vbos if any
        self.release()

        # First create VBOs for the hovering state
        self.translation_mode_lines_vbos = {}
        for state_name_and_active_index, vertices in constants.GIZMO_TRANSLATION_STATE_HOVERING_VERTEX_GROUP.items():
            self.translation_mode_lines_vbos[state_name_and_active_index] = self.ctx.buffer(vertices.tobytes())

        # Create one vao per vbo
        for _, vbo in self.translation_mode_lines_vaos:
            if vbo is not None:
                vbo.release()

        self.translation_mode_lines_vaos = {}
        for state_name_and_active_index, vbo in self.translation_mode_lines_vbos.items():
            self.translation_mode_lines_vaos[state_name_and_active_index] = self.ctx.simple_vertex_array(
                self.program_lines,
                vbo,
                'aPositionSize',
                'aColor')

        # Generate guides for when the object is being moved along the axes
        self.axis_guide_vbo = self.ctx.buffer(constants.GIZMO_TRANSLATION_VERTICES_AXIS_GUIDE.tobytes())
        self.axis_guide_vao = self.ctx.simple_vertex_array(
                self.program_lines,
                self.axis_guide_vbo,
                'aPositionSize',
                'aColor')

        # Center
        center_data = self.generate_center_vertex_data(
            radius=constants.GIZMO_CENTER_RADIUS,
            color=(0.7, 0.7, 0.7, constants.GIZMO_ALPHA))
        self.center_triangles_vbo = self.ctx.buffer(center_data.tobytes())
        self.center_triangles_vao = self.ctx.vertex_array(
            self.program_triangles,
            [
                (self.center_triangles_vbo, '3f 4f', 'aPosition', 'aColor')  # Assuming each vertex is 8 floats (4 bytes each)
            ]
        )
        center_data = self.generate_center_vertex_data(
            radius=constants.GIZMO_CENTER_RADIUS,
            color=(0.8, 0.8, 0.0, constants.GIZMO_ALPHA))
        self.center_triangles_highlight_vbo = self.ctx.buffer(center_data.tobytes())
        self.center_triangles_highlight_vao = self.ctx.vertex_array(
            self.program_triangles,
            [
                (self.center_triangles_highlight_vbo, '3f 4f', 'aPosition', 'aColor')
            ]
        )

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
        self.ctx.line_width = 3.0  # TODO: Figure out how this affects the line rendering

        if self.gizmo_mode == constants.GIZMO_MODE_TRANSLATION:

            # TODO: Resolve Z-fighting here by rendering the axis guide and clearing the depth buffer once more (?)
            self.translation_mode_lines_vaos[(self.state, self.active_index)].render(moderngl.LINES)

            self.program_triangles['uViewProjMatrix'].write(transform_matrix)

            if self.state in (constants.GIZMO_STATE_HOVERING_CENTER, constants.GIZMO_STATE_DRAGGING_CENTER):
                self.center_triangles_highlight_vao.render(moderngl.TRIANGLES)
            else:
                self.center_triangles_vao.render(moderngl.TRIANGLES)

            if self.state == constants.GIZMO_STATE_DRAGGING_AXIS:
                world_transform_matrix = projection_matrix * view_matrix * mat4(1.0)
                self.program_lines['uViewProjMatrix'].write(world_transform_matrix)
                self.axis_guide_vao.render(moderngl.LINES)

        if self.gizmo_mode == constants.GIZMO_MODE_ROTATION:
            pass

        if self.gizmo_mode == constants.GIZMO_MODE_SCALE:
            pass

    # =========================================================================
    #                           Input Callbacks
    # =========================================================================

    def handle_event_mouse_button_press(self,
                                        button: int,
                                        ray_origin: vec3,
                                        ray_direction: vec3,
                                        model_matrix: mat4,
                                        component: Any):

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

                # Update data on the Axis guide to highlight which axis is being dragged
                if self.axis_guide_vbo:
                    p0 = self.original_axes_p0[self.active_index]
                    p1 = self.original_axes_p1[self.active_index]
                    new_data = np.array(
                        [  # These values are placeholders. They are overwritten dynamically
                            [p0.x, p0.y, p0.z, constants.GIZMO_AXIS_GUIDE_LINE_WIDTH, 0.0, 0.0, 0.0, 0.8],
                            [p1.x, p1.y, p1.z, constants.GIZMO_AXIS_GUIDE_LINE_WIDTH, 0.0, 0.0, 0.0, 0.8]
                        ],
                        dtype='f4'
                    )

                    # Set colour corresponding to the axis
                    new_data[:, 4 + self.active_index] = 1.0
                    self.axis_guide_vbo.write(new_data.tobytes())

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
                self.plane_offset_point -= self.original_position
                self.state = constants.GIZMO_STATE_DRAGGING_PLANE
                return

            if self.state == constants.GIZMO_STATE_HOVERING_CENTER:
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
                    self.state = constants.GIZMO_STATE_DRAGGING_CENTER
                return

    def handle_event_mouse_button_release(self,
                                          button: int,
                                          ray_origin: vec3,
                                          ray_direction: vec3,
                                          model_matrix: mat4,
                                          component: Any):

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

    def handle_event_mouse_move(self,
                                event_data: tuple,
                                ray_origin: vec3,
                                ray_direction: vec3,
                                model_matrix: mat4,
                                component: Any) -> mat4:
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
            closest_state = constants.GIZMO_STATE_HOVERING_PLANE
            closest_index = active_plane_index

        # Update state and active index
        self.state = closest_state
        self.active_index = closest_index

        return None

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
        if self.state == constants.GIZMO_STATE_DRAGGING_CENTER:

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

        if self.state == constants.GIZMO_STATE_DRAGGING_AXIS and self.active_index > -1:

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

        if self.state == constants.GIZMO_STATE_DRAGGING_PLANE and self.active_index > -1:

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
            delta_vector = new_plane_point - self.plane_offset_point

            # Create a new translation matrix
            new_model_matrix = mat4(self.original_model_matrix)
            new_model_matrix[3] = vec4(delta_vector, 1.0)

            return new_model_matrix

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

        if center_dist2 < (self.gizmo_scale * constants.GIZMO_CENTER_RADIUS) ** 2:

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

        # Resolve which plane patch is the closest
        if len(plane_intersections) > 0:
            closest_plane_patch = min(plane_intersections, key=lambda x: x[3])  # x[3] is the t value
            active_index = closest_plane_patch[0]
            ray_t = closest_plane_patch[3]
            is_hovering = True

        return is_hovering, ray_t, active_index

    def check_disk_hovering(self, ray_origin: vec3, ray_direction: vec3, model_matrix: mat4) -> tuple:
        pass

    def release(self):

        for _, vao in self.translation_mode_lines_vaos.items():
            if vao:
                vao.release()

        for _, vbo in self.translation_mode_lines_vbos.items():
            if vbo:
                vbo.release()

    # =============================================================
    #                   Geometry functions
    # =============================================================

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
            imgui.text(f"Mode: {self.gizmo_mode}")
            imgui.text(f"State: {str(self.state)}")
            imgui.text(f"Axis: {self.active_index}")
            imgui.text(f"Scale: {self.gizmo_scale}")

