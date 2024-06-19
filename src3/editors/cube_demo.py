import numpy as np
import moderngl
import glfw
import imgui

from pyrr import Matrix44, Vector3

from src3.editors.editor import Editor


"""
Written by ChatGPT4o and fixed by yours truly. Bloody transformer forgot to initialise the framebuffer!
"""


class CubeDemo(Editor):
    label = "Cube Demo"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.program = self.shader_library.shaders["cube_simple.glsl"].program
        self.cube_vao = self.create_cube_vao()
        self.model_matrix = Matrix44.identity()
        self.camera_matrix = Matrix44.look_at(
            eye=Vector3([3.0, 3.0, 3.0]),
            target=Vector3([0.0, 0.0, 0.0]),
            up=Vector3([0.0, 0.0, 1.0])
        )
        self.projection_matrix = Matrix44.perspective_projection(
            fovy=45.0,
            aspect=1.0,
            near=0.1,
            far=100.0
        )
        self.initial_window_size = (400, 400)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((400, 400), 3),
            depth_attachment=self.ctx.depth_texture((400, 400)),
        )

    def create_cube_vao(self):
        vertices = np.array([
            -1.0, -1.0, -1.0, 0.0, 0.0, -1.0,
            1.0, -1.0, -1.0, 0.0, 0.0, -1.0,
            1.0, 1.0, -1.0, 0.0, 0.0, -1.0,
            -1.0, 1.0, -1.0, 0.0, 0.0, -1.0,
            -1.0, -1.0, 1.0, 0.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 0.0, 0.0, 1.0,
            -1.0, 1.0, 1.0, 0.0, 0.0, 1.0,
            -1.0, -1.0, -1.0, 0.0, -1.0, 0.0,
            1.0, -1.0, -1.0, 0.0, -1.0, 0.0,
            1.0, -1.0, 1.0, 0.0, -1.0, 0.0,
            -1.0, -1.0, 1.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, -1.0, 0.0, 1.0, 0.0,
            1.0, 1.0, -1.0, 0.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 0.0, 1.0, 0.0,
            -1.0, 1.0, 1.0, 0.0, 1.0, 0.0,
            -1.0, -1.0, -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 1.0, -1.0, 0.0, 0.0,
            -1.0, -1.0, 1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 1.0, 0.0, 0.0,
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            8, 9, 10, 10, 11, 8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20,
        ], dtype=np.uint32)

        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        vao = self.ctx.vertex_array(
            self.program,
            [
                (vbo, '3f 3f', 'in_position', 'in_normal')
            ],
            index_buffer=ibo
        )
        return vao

    def update(self, elapsed_time: float):
        self.fbo.use()
        self.ctx.clear(0.2, 0.3, 0.3)
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.program['m_model'].write(self.model_matrix.astype('f4').tobytes())
        self.program['m_camera'].write(self.camera_matrix.astype('f4').tobytes())
        self.program['m_proj'].write(self.projection_matrix.astype('f4').tobytes())
        self.program['color'].value = (1.0, 0.5, 0.31, 1.0)

        self.cube_vao.render(moderngl.TRIANGLES)

        # Render the UI on top of the 3D scene
        self.render_ui()

    def render_ui(self):
        """Render the UI"""
        imgui.begin("Cube Demo", True)
        imgui.set_window_size(*self.initial_window_size)

        imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size)

        imgui.text("Use arrow keys to move the cube")

        imgui.end()

    def handle_event_keyboard_press(self, event_data: tuple):
        key, scancode, mods = event_data

        if key == glfw.KEY_UP:
            self.model_matrix *= Matrix44.from_translation([0.0, 0.0, 0.1])
        elif key == glfw.KEY_DOWN:
            self.model_matrix *= Matrix44.from_translation([0.0, 0.0, -0.1])
        elif key == glfw.KEY_LEFT:
            self.model_matrix *= Matrix44.from_translation([-0.1, 0.0, 0.0])
        elif key == glfw.KEY_RIGHT:
            self.model_matrix *= Matrix44.from_translation([0.1, 0.0, 0.0])
