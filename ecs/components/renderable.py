import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.systems.render_system.shader_program_library import ShaderProgramLibrary


class Renderable(Component):

    _type = constants.COMPONENT_TYPE_RENDERABLE

    __slots__ = [
        "render_layer",
        "vaos",
        "visible",
        "shadow_caster",
        "_gpu_initialised"
    ]

    def __init__(self, **kwargs):

        super().__init__()

        self.render_layer = 0
        self.vaos = {}

        # Flags
        self.visible = kwargs.get("visible", True)
        self.shadow_caster = kwargs.get("shadow_caster", True)

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

        self.gpu_initialised = True

    def release(self):
        for _, vao in self.vaos:
            vao.release()

