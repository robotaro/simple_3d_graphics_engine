import moderngl
import glm
import numpy as np
from src3.shader_loader import ShaderLoader

class Gizmo3D:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 output_fbo: moderngl.Framebuffer):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.output_fbo = output_fbo
        self.program = shader_loader.get_program("gizmo_shader.glsl")

        self.helper_fbo = self.ctx.framebuffer(
            depth_attachment=self.output_fbo.depth_attachment,
        )

        # Prepare the gizmo vertices for the axes (x, y, z)
        # Each axis will have a line with start and end points, and a specified width
        axis_length = 1.0
        line_width = 3.0

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
        self.vbo = self.ctx.buffer(gizmo_vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'aPositionSize', 'aColor')

    def update_input(self, mouse_x: float, mouse_y: float):
        pass

    def render(self, view_matrix: glm.mat4, projection_matrix: glm.mat4, entity_transform: glm.mat4):
        # Bind the helper framebuffer to clear the depth buffer
        self.helper_fbo.use()
        self.helper_fbo.clear(depth=True)

        # Bind the output framebuffer to render the gizmo
        self.output_fbo.use()

        # Calculate the camera position from the view matrix
        camera_position = glm.inverse(view_matrix) * glm.vec4(0.0, 0.0, 0.0, 1.0)
        camera_position = glm.vec3(camera_position)  # Convert to vec3

        # Determine the scale factor to keep the gizmo a constant size on the screen
        # This assumes the gizmo is located at the origin
        gizmo_position = glm.vec3(entity_transform[3])
        distance = glm.length(camera_position - gizmo_position)
        scale_factor = distance * 0.1  # Adjust 0.1 to change the size of the gizmo on screen

        # Apply the scale factor to the entity transform
        scale_matrix = glm.scale(glm.mat4(1.0), glm.vec3(scale_factor))
        transform_matrix = projection_matrix * view_matrix * entity_transform * scale_matrix

        # Pass the transform matrix to the shader
        self.program['uViewProjMatrix'].write(transform_matrix.to_bytes())

        # Pass the viewport size to the geometry shader
        viewport_size = (self.output_fbo.viewport[2], self.output_fbo.viewport[3])
        self.program['uViewport'].value = viewport_size

        # Set the line width
        self.ctx.line_width = 3.0

        # Render the gizmo axes
        self.vao.render(moderngl.LINES)
