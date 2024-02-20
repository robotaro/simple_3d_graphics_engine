import logging
import moderngl
from collections import deque

from src2.modules.module import Module


class SceneEditor(Module):

    label = "Scene Editor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        """self.cube = geometry.cube(size=(2, 2, 2))
        self.prog = self.load_program('programs/cube_simple.glsl')
        self.prog['color'].value = (1.0, 1.0, 1.0, 1.0)
        self.prog['m_camera'].write(Matrix44.identity(dtype='f4'))
        self.prog['m_proj'].write(Matrix44.perspective_projection(75, 1.0, 1, 100, dtype='f4'))

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((512, 512), 4),
            depth_attachment=self.ctx.depth_texture((512, 512)),
        )
        # Ensure imgui knows about this texture
        # This is the color layer in the framebuffer
        self.imgui.register_texture(self.fbo.color_attachments[0])"""

    def update(self, elapsed_time: float) -> bool:

        # Render scene
        h = 0

        # Render GUI

        pass

    def render_main(self):
        pass

    def handle_event_window_drop_files(self, event_data: tuple):
        print(event_data)
