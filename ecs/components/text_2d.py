import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.shader_program_library import ShaderProgramLibrary


class Text2D(Component):

    _type = "text_2d"

    __slots__ = [
        "render_layer",
        "visible",
        "vao",
        "vbo",
        "_gpu_initialised"
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.render_layer = 0
        self.visible = True
        self.vao = None
        self.vbo = None
        self._gpu_initialised = False

    def initialise_on_gpu(self,
                          ctx: moderngl.Context,
                          shader_library: ShaderProgramLibrary):

        if self._gpu_initialised:
            return

        self.vbo = ctx.buffer(reserve=1000)  # TODO: Check this size
        program = shader_library[constants.SHADER_PROGRAM_TEXT_2D]
        self.vao = ctx.vertex_array(program,
                                    ("2f 2f 2f 2f"),
                                    ["in_position", "in_size", "in_uv_position", "in_uv_size"])

        self._gpu_initialised = True

    def set_text(self, text: str) -> None:

        if not self._gpu_initialised:
            return

        pass

    def release(self):
        if self.vbo:
            self.vbo.release()

        if self.vao:
            self.vbo.release()

