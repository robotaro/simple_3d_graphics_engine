import moderngl

from src.core import constants
from src.components.component import Component
from src.systems.render_system.shader_program_library import ShaderProgramLibrary
from src.systems.render_system.font_library import FontLibrary


class Text2D(Component):

    _type = "text_2d"

    __slots__ = [
        "font_name",
        "position",
        "render_layer",
        "visible",
        "vao",
        "vbo",
        "text",
        "_text_updated",
        "_gpu_initialised"
    ]

    def __init__(self, parameters: dict):

        super().__init__(parameters=parameters)

        # TODO: User standard methof for retrieving parameter values
        self.font_name = parameters["font_name"]
        self.position = (10, 10)
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

        self.vbo = ctx.buffer(reserve=constants.FONT_VBO_BUFFER_RESERVE)  # TODO: Check this size
        program = shader_library[constants.SHADER_PROGRAM_TEXT_2D]

        self.vao = ctx.vertex_array(program, self.vbo, "in_position", "in_size", "in_uv_min", "in_uv_max")

        self._gpu_initialised = True

    def update_buffer(self, font_library: FontLibrary):

        if not self._gpu_initialised or not self._text_updated:
            return

        text_data = font_library.generate_text_vbo_data(font_name=self.font_name,
                                                        text=self.text,
                                                        position=self.position)

        self.vbo.write(text_data[:, :8].tobytes())

    def set_text(self, text: str) -> None:
        self.text = text
        self._text_updated = True

    def release(self):
        if self.vbo:
            self.vbo.release()

        if self.vao:
            self.vbo.release()

