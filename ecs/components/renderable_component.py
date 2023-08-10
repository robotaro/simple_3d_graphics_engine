import moderngl

from ecs.components.component import Component
from ecs.systems.render_system.shader_library import ShaderLibrary


class Renderable(Component):

    def __init__(self):
        self.mode = None  # TODO: Add modes to the material rendering
        self.diffuse_color = (0.5, 0.5, 0.5)
        self.ambient = 0.5
        self.specular = 0.5

        # VAOs
        self.vao_fragment_picking_pass = None
        self.vao_forward_pass = None
        self.vao_outline_pass = None

    def create_vaos(self, ctx: moderngl.Context, shader_library: ShaderLibrary, vbo_list: list):
        # This is effecivelly the "make_renderable"

        self.vao_forward_pass = ctx.vertex_array("forward_pass", vbo_list)

    @Node.once
    def make_renderable(self, mlg_context: moderngl.Context, shader_library: ShaderLibrary):

        print(f"[{self._type} | {self.name}] make_renderable")

        # TODO: - Check if I need to upload data here or leave it to uploaded buffers
        #       - Check if I need to set these to dynamic

        vbo_list = []

        # Create VBOs
        if self.vertices is not None:
            self.vbo_vertices = mlg_context.buffer(self.vertices.astype("f4").tobytes())
            vbo_list.append((self.vbo_vertices, "3f", "in_vert"))

        if self.normals is not None:
            self.vbo_normals = mlg_context.buffer(self.normals.astype("f4").tobytes())
            vbo_list.append((self.vbo_normals, "3f", "in_normal"))

        program = shader_library[self.forward_pass_program_name]

        if self.faces is None:
            self.vao = mlg_context.vertex_array(program, vbo_list)
        else:
            self.ibo_faces = mlg_context.buffer(self.faces.astype("i4").tobytes())
            self.vao = mlg_context.vertex_array(program, vbo_list, self.ibo_faces)