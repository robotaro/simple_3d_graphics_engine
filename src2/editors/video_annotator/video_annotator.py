import glfw
import numpy as np
import moderngl
import imgui
from collections import deque
import imageio
import cv2
import matplotlib.pyplot as plt

from src2.core import constants
from src2.editors.editor import Editor

from src2.editors.video_annotator.ui_timeline_editor import UITimelineEditor


class VideoAnnotator(Editor):
    label = "Video Annotator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Video player variables
        self.video_file = "F:\stuff\hentai\[SakuraCircle] Boku wa Chiisana Succubus no Shimobe - 01 (DVD 720x480 h264 AAC) [6F07860A].mkv"
        self.reader = imageio.get_reader(self.video_file, 'ffmpeg')
        self.meta_data = self.reader.get_meta_data()
        self.duration = int(self.meta_data['duration'])
        self.fps = self.meta_data['fps']
        self.current_timestamp = 0.0
        self.current_frame_index = 0
        self.frame_period = 1.0 / self.fps
        self.total_num_frames = int(self.fps * self.duration)
        self.video_playing = False
        self.frame_size = self.meta_data["size"]

        self.program = self.shader_library.programs["texture"]
        self.fullscreen_quad_vao = self.create_full_screen_quad_vao()
        self.texture = self.ctx.texture(self.frame_size, 3)  # Adjust the size as needed
        random_data = np.random.randint(0, 255, (*self.frame_size, 3)).astype('u1')  # Generate random RGBA data
        self.texture.write(data=random_data.tobytes())
        self.texture.use(location=0)

        self.initial_window_size = (self.texture.size[0] + 50, self.texture.size[1] + 100)

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(self.frame_size, 3),
            depth_attachment=self.ctx.depth_texture(self.frame_size),
        )

        # Main UI components
        self.ui_timeline_editor = UITimelineEditor()

        # Subscribe to events
        self.event_publisher.subscribe(event_type=constants.EVENT_KEYBOARD_PRESS, listener=self)

        self.update_texture(frame_index=0)

    def update_texture(self, frame_index: int) -> None:
        frame_data = self.reader.get_data(frame_index)
        self.texture.write(data=frame_data.tobytes())

    def update(self, elapsed_time: float) -> bool:

        self.fbo.use()
        self.fbo.clear(color=(0.5, 0.5, 0.5, 1.0))
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        if self.video_playing:
            self.current_timestamp += elapsed_time
            self.current_frame_index = int(self.current_timestamp * self.fps)
            if self.current_frame_index >= self.total_num_frames:
                self.current_frame_index = 0
            self.update_texture(frame_index=self.current_frame_index)

        self.texture.use(location=0)
        self.fullscreen_quad_vao.render()

        # Render UI to screen
        self.render_ui()

    def create_full_screen_quad_vao(self, size=(2.0, 2.0), position=(-1.0, -1.0)) -> moderngl.VertexArray:
            width, height = size
            xpos, ypos = position

            vertices = np.array([
                xpos, ypos + height, 0.0,
                xpos, ypos, 0.0,
                      xpos + width, ypos, 0.0,
                xpos, ypos + height, 0.0,
                      xpos + width, ypos, 0.0,
                      xpos + width, ypos + height, 0.0,
            ], dtype=np.float32)

            uvs = np.array([
                0.0, 1.0,
                0.0, 0.0,
                1.0, 0.0,
                0.0, 1.0,
                1.0, 0.0,
                1.0, 1.0,
            ], dtype=np.float32)

            # Create VBOs
            vbo_vertices = self.ctx.buffer(vertices.astype("f4").tobytes())
            vbo_uvs = self.ctx.buffer(uvs.astype("f4").tobytes())

            return self.ctx.vertex_array(
                    self.program,
                    [(vbo_vertices, '3f', 'in_position'),
                     (vbo_uvs, '2f', 'in_texcoord_0')])

    def render_ui(self):
        """Render the UI"""
        imgui.begin("Video Frame", True)
        imgui.set_window_size(*self.initial_window_size)

        imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size)

        slider_activated, self.current_frame_index = imgui.slider_int(
            "Frame",
            self.current_frame_index,
            0,
            self.total_num_frames - 1)

        if slider_activated:
            self.current_timestamp = self.current_frame_index / self.fps
            self.update_texture(frame_index=self.current_frame_index)

        self.ui_timeline_editor.render()

        # Render the full-screen quad

        imgui.end()

    def handle_event_keyboard_press(self, key, scancode, mods):

        if key == glfw.KEY_SPACE:
            self.video_playing ^= True
            self.logger.debug(f"Playing video: {self.video_playing}")

        if key == glfw.KEY_RIGHT:
            self.current_frame_index += 1
            self.current_timestamp = self.current_frame_index / self.fps

        if key == glfw.KEY_LEFT:
            self.current_frame_index -= 1
            self.current_timestamp = self.current_frame_index / self.fps
