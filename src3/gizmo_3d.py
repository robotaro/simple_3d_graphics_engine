import moderngl
import glm
import numpy as np
from src3 import constants
from glm import vec3, mat4

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

        self.gizmo_scale = 1.0
        self.gizmo_mode = constants.GIZMO_MODE_TRANSLATION
        self.gizmo_state = constants.GIZMO_STATE_INACTIVE
        self.gizmo_active_axis = 0
        self.gizmo_translation_offset_point = vec3(0, 0, 0)
        self.axes_dist2 = [0.0] * 3

        self.translation_vector = vec3(0)
        self.translation_axis_segment_p0 = vec3(0)
        self.translation_axis_segment_p1 = vec3(0)

        self.model_matrix = mat4(1.0)
        self.ray_origin = glm.vec3(0.0)
        self.ray_direction = glm.vec3(0.0)

    def update_and_render(self,
                          view_matrix: glm.mat4,
                          projection_matrix: glm.mat4,
                          model_matrix: glm.mat4,
                          ray_origin: vec3,
                          ray_direction: vec3) -> mat4:

        # Story updated info to be used by callbacks later
        self.model_matrix = model_matrix
        self.ray_origin = ray_origin
        self.ray_direction = ray_direction

        new_model_matrix = None

        if self.gizmo_mode == constants.GIZMO_MODE_TRANSLATION:
            new_model_matrix = self.render_gizmo_translation_mode(view_matrix=view_matrix,
                projection_matrix=projection_matrix,
                model_matrix=model_matrix,
                ray_origin=ray_origin,
                ray_direction=ray_direction)

        if self.gizmo_mode == constants.GIZMO_MODE_ROTATION:
            pass

        if self.gizmo_mode == constants.GIZMO_MODE_SCALE:
            pass

        return new_model_matrix

    def render_gizmo_translation_mode(self,
                                      view_matrix: glm.mat4,
                                      projection_matrix: glm.mat4,
                                      model_matrix: glm.mat4,
                                      ray_origin: vec3,
                                      ray_direction: vec3) -> mat4:

        new_model_matrix = None

        # Calculate the camera position from the view matrix
        camera_position = glm.inverse(view_matrix) * glm.vec4(0.0, 0.0, 0.0, 1.0)
        camera_position = glm.vec3(camera_position)  # Convert to vec3

        # Determine the scale factor to keep the gizmo a constant size on the screen
        gizmo_position = glm.vec3(model_matrix[3])
        distance = glm.length(camera_position - gizmo_position)
        self.gizmo_scale = distance * self.gizmo_size_on_screen

        # Update vertices with the new scale factor
        self.update_translation_vertices(self.gizmo_scale)

        # No need to apply the scale to the entity matrix
        transform_matrix = projection_matrix * view_matrix * model_matrix

        if self.gizmo_state == constants.GIZMO_STATE_START_DRAGGING:

            # Generate a long segment representing the axis we're translating
            selected_axis_direction = vec3(model_matrix[self.gizmo_active_axis])
            self.translation_axis_segment_p0 = gizmo_position - 500.0 * selected_axis_direction
            self.translation_axis_segment_p1 = gizmo_position + 500.0 * selected_axis_direction

            # Get offset on axis where you first clicked, the "translation offset"
            entity_position = vec3(self.model_matrix[3])
            self.gizmo_translation_offset_point, _ = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=self.translation_axis_segment_p0,
                p1=self.translation_axis_segment_p1
            )
            self.gizmo_translation_offset_point -= entity_position
            self.gizmo_state = constants.GIZMO_STATE_DRAGGING

        if self.gizmo_state == constants.GIZMO_STATE_DRAGGING:
            entity_position = glm.vec3(self.model_matrix[3])
            axis_direction = glm.vec3(self.model_matrix[self.gizmo_active_axis])

            nearest_point_on_axis, _ = math_3d.nearest_point_on_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=entity_position,
                p1=entity_position + axis_direction
            )

            self.translation_vector = nearest_point_on_axis - (entity_position + self.gizmo_translation_offset_point)
            new_model_matrix = glm.translate(self.model_matrix, self.translation_vector)

        else:  # HOVERING OR INACTIVE
            self.axes_dist2 = [math_3d.distance2_ray_segment(
                ray_origin=ray_origin,
                ray_direction=ray_direction,
                p0=gizmo_position,
                p1=glm.vec3(model_matrix[i]) * self.gizmo_scale + gizmo_position) for i in range(3)]

            shortest_dist_index = np.argmin(self.axes_dist2)

            if self.axes_dist2[shortest_dist_index] < self.gizmo_scale * constants.GIZMO_AXIS_DETECTION_RADIUS:
                self.gizmo_state = constants.GIZMO_STATE_HOVERING
                self.gizmo_active_axis = shortest_dist_index
            else:
                self.gizmo_state = constants.GIZMO_STATE_INACTIVE
                self.gizmo_active_axis = -1

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

        return new_model_matrix

    def generate_translation_vertices(self):
        # Create buffer and vertex array for the gizmo, initially with unit length axes
        axis_length = 1.0
        line_width = 5.0

        # x-axis (red)
        x_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 1.0, 0.0, 0.0, 1.0,
            axis_length, 0.0, 0.0, line_width, 1.0, 0.0, 0.0, 1.0
        ]

        # y-axis (green)
        y_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 0.0, 1.0, 0.0, 1.0,
            0.0, axis_length, 0.0, line_width, 0.0, 1.0, 0.0, 1.0
        ]

        # z-axis (blue)
        z_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 0.0, 0.0, 1.0, 1.0,
            0.0, 0.0, axis_length, line_width, 0.0, 0.0, 1.0, 1.0
        ]

        # Combine all vertices
        gizmo_vertices = np.array(x_axis_vertices + y_axis_vertices + z_axis_vertices, dtype='f4')

        # Create buffer and vertex array for the gizmo
        self.translation_vbo = self.ctx.buffer(gizmo_vertices.tobytes())
        self.translation_vao = self.ctx.simple_vertex_array(self.program, self.translation_vbo, 'aPositionSize', 'aColor')

    def update_translation_vertices(self, scale_factor):
        # Scale the vertices directly
        axis_length = scale_factor
        line_width = 5.0

        # x-axis (red)
        x_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 1.0, 0.0, 0.0, 1.0,
            axis_length, 0.0, 0.0, line_width, 1.0, 0.0, 0.0, 1.0
        ]

        # y-axis (green)
        y_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 0.0, 1.0, 0.0, 1.0,
            0.0, axis_length, 0.0, line_width, 0.0, 1.0, 0.0, 1.0
        ]

        # z-axis (blue)
        z_axis_vertices = [
            0.0, 0.0, 0.0, line_width, 0.0, 0.0, 1.0, 1.0,
            0.0, 0.0, axis_length, line_width, 0.0, 0.0, 1.0, 1.0
        ]

        # Combine all vertices
        gizmo_vertices = np.array(x_axis_vertices + y_axis_vertices + z_axis_vertices, dtype='f4')

        # Update the VBO with the new vertices
        self.translation_vbo.write(gizmo_vertices.tobytes())

    def handle_event_mouse_button_press(self, button: int, ray_origin: vec3, ray_direction: vec3):

        if button == constants.MOUSE_LEFT and self.gizmo_state == constants.GIZMO_STATE_HOVERING:
            self.gizmo_state = constants.GIZMO_STATE_START_DRAGGING

    def handle_event_mouse_button_release(self, button: int):
        if button == constants.MOUSE_LEFT:
            self.gizmo_state = constants.GIZMO_STATE_INACTIVE

    def handle_event_keyboard_press(self, event_data: tuple):
        key, modifiers = event_data
        # Add code here as needed

    def handle_event_keyboard_release(self, event_data: tuple):
        key, modifiers = event_data
        # Add code here as needed

    def handle_event_mouse_move(self, event_data: tuple):
        x, y, dx, dy = event_data
        # Add code here as needed

    def handle_event_mouse_drag(self, event_data: tuple):
        x, y, dx, dy = event_data

