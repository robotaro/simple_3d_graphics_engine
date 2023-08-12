import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.systems.render_system.shader_library import ShaderLibrary


class Renderable(Component):

    def __init__(self):

        self.render_layer = 0
        self.vao_fragment_picking_pass = None
        self.vao_forward_pass = None
        self.vao_outline_pass = None

        self._gpu_initialised = False

    def initialise_on_gpu(self,
                          ctx: moderngl.Context,
                          shader_library: ShaderLibrary,
                          vbo_tuple_list: list,
                          ibo_faces=None):

        # TODO: Think of a better place  to put this utility function
        def create_vao(ibo_faces: moderngl.Buffer):
            if ibo_faces is None:
                return ctx.vertex_array(program, vbo_tuple_list)
            else:
                return ctx.vertex_array(program, vbo_tuple_list, ibo_faces)

        if self._gpu_initialised:
            return

        program = shader_library[constants.RENDER_SYSTEM_PROGRAM_FORWARD_PASS]
        self.vao_forward_pass = create_vao(ibo_faces=ibo_faces)

        self._gpu_initialised = True

    def release(self):
        if self.vao_fragment_picking_pass:
            self.vao_fragment_picking_pass.release()

        if self.vao_forward_pass:
            self.vao_forward_pass.release()

        if self.vao_outline_pass:
            self.vao_outline_pass.release()