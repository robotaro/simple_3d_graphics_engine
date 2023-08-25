import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.shader_program_library import ShaderProgramLibrary


class Renderable(Component):

    _type = "renderable"

    __slots__ = [
        "render_layer",
        "vaos",
        "visible",
        "_gpu_initialised"
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.render_layer = 0
        self.visible = True
        self.vaos = {}
        self._gpu_initialised = False

    def initialise_on_gpu(self,
                          ctx: moderngl.Context,
                          shader_library: ShaderProgramLibrary,
                          vbo_tuple_list: list,
                          program_name_list: list,
                          ibo_faces=None):

        if self._gpu_initialised:
            return

        for program_name in program_name_list:

            program = shader_library[program_name]

            # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
            if ibo_faces is None:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_tuple_list)
            else:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_tuple_list, ibo_faces)

        self._gpu_initialised = True

    def release(self):
        for _, vao in self.vaos:
            vao.release()

