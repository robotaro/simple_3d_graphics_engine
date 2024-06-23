import os.path

import numpy as np
import moderngl
import glfw
import imgui

from pyrr import Matrix44, Vector3

from src3 import constants
from src3.editor import Editor
from src3.io.gltf_reader import GLTFReader

"""
Written by ChatGPT4o and fixed by yours truly. Bloody transformer forgot to initialise the framebuffer!
"""


class GLTFLoadDemo(Editor):
    label = "GLTF Load Demo"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.framebuffer_size = (400, 400)
        self.program = self.shader_loader.shaders["crate_example.glsl"].program
        self.mvp = self.program['Mvp']
        self.light = self.program['Light']
        self.aspect_ratio = self.framebuffer_size[0] / self.framebuffer_size[1]
        self.vao = self.create_model_naive()

        self.model_matrix = Matrix44.identity()
        self.camera_matrix = Matrix44.look_at(
            eye=Vector3([100.0, 100.0, 100.0]),
            target=Vector3([0.0, 0.0, 0.0]),
            up=Vector3([0.0, 0.0, 1.0])
        )
        self.projection_matrix = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(self.framebuffer_size, 3),
            depth_attachment=self.ctx.depth_texture(self.framebuffer_size),
        )

    def create_model_naive(self):

        reader = GLTFReader()

        gltf_fpath = os.path.join(constants.RESOURCES_DIR, "meshes", "Duckpaa6lgsfsngq0i1w.glb")
        reader.load(gltf_fpath=gltf_fpath)
        meshes = reader.get_meshes()

        vertices = np.concatenate([meshes[-1]["attributes"]["POSITION"] * 0.01,
                                   meshes[-1]["attributes"]["NORMAL"]], axis=1)
        indices = meshes[-1]["indices"].astype(np.uint32)

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

    def setup(self) -> bool:
        return True

    def update(self, time: float, elapsed_time: float):

        angle = time
        self.fbo.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)  # This is the global state! It will be applied to any operations after this, including the framebuffer!
        self.fbo.use()

        camera_pos = (np.cos(angle) * 3.0, np.sin(angle) * 3.0, 2.0)

        lookat = Matrix44.look_at(
            camera_pos,
            (0.0, 0.0, 0.5),
            (0.0, 0.0, 1.0),
        )

        self.mvp.write((self.projection_matrix * lookat).astype('f4'))
        self.light.value = camera_pos
        self.vao.render()

        # Render the UI on top of the 3D scene
        self.render_ui()

    def shutdown(self):
        self.vao.release()
        self.logger.info("GLTF Demo shutdown complete")

    def render_ui(self):
        """Render the UI"""
        imgui.new_frame()
        imgui.begin(GLTFLoadDemo.label, True)
        imgui.set_window_size(*self.framebuffer_size)

        imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size, uv0=(0, 1), uv1=(1, 0))

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

