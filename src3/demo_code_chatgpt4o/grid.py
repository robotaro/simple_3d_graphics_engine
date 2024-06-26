import moderngl
import moderngl_window
import numpy as np
from moderngl_window import geometry
from pyrr import Matrix44

class InfiniteGrid(moderngl_window.WindowConfig):
    gl_version = (4, 3)
    title = "Infinite Grid with Variable Line Width"
    window_size = (800, 600)
    aspect_ratio = 16 / 9
    resource_dir = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\src3\demo_code_chatgpt4o"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.load_program(
            vertex_shader='grid.vert',
            fragment_shader='grid.frag'
        )

        # Define a large plane for the grid
        self.grid = self.create_plane(self.ctx, size=(200.0, 200.0))

        # Uniforms
        self.prog['grid_color'].value = (0.8, 0.8, 0.8)
        self.prog['bg_color'].value = (0.0, 0.0, 0.0)  # Black background
        self.prog['x_axis_color'].value = (1.0, 0.0, 0.0)  # Red for X axis
        self.prog['z_axis_color'].value = (0.0, 0.0, 1.0)  # Blue for Z axis
        self.prog['grid_spacing'].value = 1.0
        self.prog['line_width'].value = 0.01
        self.prog['fog_start'].value = 25.0
        self.prog['fog_end'].value = 40.0

        # Projection matrix
        self.proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
        self.prog['m_proj'].write(self.proj.astype('f4'))

        # View matrix
        self.view = Matrix44.look_at(
            (10.0, 10.0, 10.0),  # Camera position
            (0.0, 0.0, 0.0),  # Look at point
            (0.0, 1.0, 0.0)  # Up vector
        )
        self.prog['m_view'].write(self.view.astype('f4'))

        # Model matrix
        self.model = Matrix44.identity()
        self.prog['m_model'].write(self.model.astype('f4'))

    def create_plane(self, ctx, size=(200.0, 200.0)):
        width, height = size
        vertices = np.array([
            [-width / 2, 0.0, -height / 2],
            [width / 2, 0.0, -height / 2],
            [-width / 2, 0.0, height / 2],
            [width / 2, 0.0, height / 2],
        ], dtype='f4')
        indices = np.array([0, 1, 2, 2, 1, 3], dtype='i4')

        vbo = ctx.buffer(vertices)
        ibo = ctx.buffer(indices)

        vao_content = [
            (vbo, '3f', 'in_position'),
        ]

        vao = ctx.vertex_array(self.prog, vao_content, ibo)

        return vao

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.0, 0.0, 0.0)  # Clear to black
        self.prog['m_view'].write(self.view.astype('f4'))
        self.grid.render(moderngl.TRIANGLES)

    def key_event(self, key, action, modifiers):
        # Basic camera control
        if key == self.wnd.keys.W:
            self.view = self.view * Matrix44.from_translation((0, 0, 0.1))
        elif key == self.wnd.keys.S:
            self.view = self.view * Matrix44.from_translation((0, 0, -0.1))
        elif key == self.wnd.keys.A:
            self.view = self.view * Matrix44.from_translation((0.1, 0, 0))
        elif key == self.wnd.keys.D:
            self.view = self.view * Matrix44.from_translation((-0.1, 0, 0))
        elif key == self.wnd.keys.UP:
            self.view = self.view * Matrix44.from_translation((0, -0.1, 0))
        elif key == self.wnd.keys.DOWN:
            self.view = self.view * Matrix44.from_translation((0, 0.1, 0))

        self.prog['m_view'].write(self.view.astype('f4'))


if __name__ == '__main__':
    moderngl_window.run_window_config(InfiniteGrid)