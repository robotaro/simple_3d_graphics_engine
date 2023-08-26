import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.systems.render_system.shader_program_library import ShaderProgramLibrary
from ecs.systems.render_system.font_library import FontLibrary


class Text2D(Component):

    _type = "text_2d"

    __slots__ = [
        "font_name",
        "render_layer",
        "visible",
        "vao",
        "vbo",
        "text",
        "_text_updated",
        "_gpu_initialised"
    ]

    def __init__(self, **kwargs):

        super().__init__()

        self.font_name = kwargs["font_name"]

        self.render_layer = 0
        self.visible = True
        self.vao = None
        self.vbo = None
        self.text = ""
        self._text_updated = False
        self._gpu_initialised = False

    def initialise_on_gpu(self,
                          ctx: moderngl.Context,
                          shader_library: ShaderProgramLibrary):

        if self._gpu_initialised:
            return

        self.vbo = ctx.buffer(reserve=800)  # TODO: Check this size
        program = shader_library[constants.SHADER_PROGRAM_TEXT_2D]

        self.vao = ctx.vertex_array(program, self.vbo, "in_position", "in_size", "in_uv_position", "in_uv_size")

        self._gpu_initialised = True

    def update_buffer(self, font_library: FontLibrary):

        if not self._gpu_initialised or not self._text_updated:
            return

        text_data = font_library.generate_text_vbo_data(font_name=self.font_name,
                                                        text=self.text,
                                                        position=(200, 200))

        self.vbo.write(text_data[:, :8].tobytes())

    def set_text(self, text: str) -> None:
        self.text = text
        self._text_updated = True

    def release(self):
        if self.vbo:
            self.vbo.release()

        if self.vao:
            self.vbo.release()

