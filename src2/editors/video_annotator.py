import logging
import moderngl
import imgui
from collections import deque

from src2.editors.editor import Editor


class VideoAnnotator(Editor):

    label = "Video Annotator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.program = self.shader_library["cube_simple"]
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((512, 512), 4),
            depth_attachment=self.ctx.depth_texture((512, 512)),
        )

        self.video_file = None

    def update(self, elapsed_time: float) -> bool:

        # Rotate/move cube
        #rotation = Matrix44.from_eulers((time, time, time), dtype='f4')
        #translation = Matrix44.from_translation((0.0, 0.0, -3.5), dtype='f4')
        #model = translation * rotation

        # Render cube to offscreen texture / fbo
        self.fbo.use()
        self.fbo.clear(color=(0.5, 0.5 , 0.5, 1.0))
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        #self.program['m_model'].write(model)
        #self.cube.render(self.prog)

        # Render UI to screen
        #self.wnd.use()
        self.render_ui()

    def on_imgui_top_menu(self):
        pass

    def handle_event_window_drop_files(self, event_data: tuple):
        print(event_data)

    def render_ui(self):
        """Render the UI"""

        imgui.show_test_window()

        # Create window with the framebuffer image
        imgui.begin("Custom window with Image", True)
        # Create an image control by passing in the OpenGL texture ID (glo)
        # and pass in the image size as well.
        # The texture needs to he registered using register_texture for this to work
        self.fbo.color_attachments[0].use(location=0)
        imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size)
        imgui.end()
