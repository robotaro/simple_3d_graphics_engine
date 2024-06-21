import imgui

from src3.editors.editor import Editor


class Viewer3D(Editor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fbo_size = (640, 480)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(self.fbo_size, 3),
            depth_attachment=self.ctx.depth_texture(self.fbo_size),
        )

        self.entities = []

        # System-only entities
        self.renderable_grid = None

    def setup(self) -> bool:
        return True

    def update(self, time: float, elapsed_time: float):
        self.render_ui()

    def shutdown(self):
        for entity in self.entities:
            entity.release()

    def render_ui(self):
        """Render the UI"""
        imgui.begin("Viewer 3D", True)
        imgui.set_window_size(800, 600)

        # Left Column - Menus
        with imgui.begin_group():
            with imgui.begin_list_box("", 200, 100) as list_box:
                if list_box.opened:
                    imgui.selectable("Selected", True)
                    imgui.selectable("Not Selected", False)

        imgui.same_line(spacing=20)

        # Right Column - 3D Scene
        with imgui.begin_group():
            imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size)

        imgui.end()

    