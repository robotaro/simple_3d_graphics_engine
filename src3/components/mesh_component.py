import numpy as np
import moderngl
from src3 import constants


VBO_DECLARATION_MAP = {
    # key       (buffer_data_type, buffer_data_size, shader_variable)
    "vertices": ("f4", "3f", constants.SHADER_INPUT_POSITION),
    "normals": ("f4", "3f", constants.SHADER_INPUT_NORMAL),
    "colors": ("f4", "3f", constants.SHADER_INPUT_COLOR),
    "joints": ("i4", "4i", constants.SHADER_INPUT_JOINT),
    "weights": ("f4", "4f", constants.SHADER_INPUT_WEIGHT),
    "uvs": ("f4", "2f", constants.SHADER_INPUT_UV),
    "indices": ("i4", None, None),
}


class MeshComponent:

    __slots__ = [
        "ctx",
        "vaos",
        "vbos",
        "ibo",
        "render_mode",
        "num_vertices"
    ]

    def __init__(self,
                 ctx: moderngl.Context,
                 vertices: np.ndarray,
                 normals: np.ndarray,
                 colors: np.ndarray,
                 indices: np.array,
                 render_mode=constants.MESH_RENDER_MODE_TRIANGLES):

        # TODO: Maybe the mesh should always be rendered with the same shader and always in triagles.
        #       Leave specialisations to other types of renderable components

        self.ctx = ctx
        self.vbos = {
            "vertices": self.create_vbo(vbo_name="vertices", vbo_data=vertices),
            "normals": self.create_vbo(vbo_name="normals", vbo_data=normals),
            "colors": self.create_vbo(vbo_name="colors", vbo_data=colors)}
        self.ibo = self.ctx.buffer(indices.astype("i4").tobytes()) if indices is not None else None
        self.vaos = {}
        self.render_mode = render_mode
        self.num_vertices = vertices.shape[0]

    def render(self, shader_program_name: str, num_instances=1):
        vao = self.vaos.get(shader_program_name, None)
        if vao is None:
            raise Exception(f"[ERROR] You are trying to render a mesh component with a VAO that does not exists: {shader_program_name}")

        vao.render(mode=self.render_mode, instances=num_instances)

    def update_vbo_data(self, vbo_name: str, data: np.ndarray):
        """
        You can use this up dynamically update the data in the GPU
        :param vbo_name: str, any of the buffers, like vertices, colors, etc
        :param data:
        :return:
        """
        self.vbos[vbo_name].write(data.tobytes())

    def create_vbo(self, vbo_name: str, vbo_data: np.ndarray):

        if vbo_data is None:
            return None
        data_type = VBO_DECLARATION_MAP[vbo_name][0]
        return self.ctx.buffer(vbo_data.astype(data_type).tobytes())

    def create_vao(self, shader_program_name: str, shader_program: moderngl.Program):

        # Each vbo has its own configuration, so a list must be made for all before you create each VAO
        vbo_declaration_list = []
        for vbo_name, vbo_object in self.vbos.items():
            if vbo_object is None:
                continue

            data_size = VBO_DECLARATION_MAP[vbo_name][1]
            shader_variable = VBO_DECLARATION_MAP[vbo_name][2]
            vbo_declaration_list.append((vbo_object, data_size, shader_variable))

        self.vaos[shader_program_name] = self.ctx.vertex_array(shader_program, vbo_declaration_list, self.ibo)

    def release(self):

        for _, vao in self.vaos.items():
            vao.release()

        for _, vbo in self.vbos.items():
            vbo.release()
