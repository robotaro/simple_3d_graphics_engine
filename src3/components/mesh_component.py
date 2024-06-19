import numpy as np
import moderngl
from src3 import constants

from src2.core import meshes_3d
from src.core.data_group import DataGroup

VBO_DECLARATION_MAP = {
    # key       (buffer_data_type, buffer_data_size, shader_variable)
    "vertices": ("f4", "3f", constants.SHADER_INPUT_VERTEX),
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
        "render_mode",
        "visible"
    ]

    def __init__(self,
                 ctx: moderngl.Context,
                 vertices: np.ndarray,
                 normals: np.ndarray,
                 colors: np.ndarray,
                 indices: np.array,
                 render_mode=constants.MESH_RENDER_MODE_TRIANGLES):

        self.ctx = ctx
        self.vbos = {
            "vertices": self.create_vbo(vbo_name="vertices", vbo_data=vertices),
            "normals": self.create_vbo(vbo_name="normals", vbo_data=normals),
            "colors": self.create_vbo(vbo_name="colors", vbo_data=colors),
            "indices": self.create_vbo(vbo_name="indices", vbo_data=indices)
        }
        self.vaos = {}
        self.render_mode = render_mode

    def render(self, program_name: str, num_instances=1):
        vao = self.vaos.get(program_name, None)
        if vao is None:
            raise Exception(f"[ERROR] You are trying to render a mesh component with a VAO that does not exists: {program_name}")

        vao.render(mode=self.render_mode, instances=num_instances)

    def upload_vbo_data(self, vbo_name: str, data: np.ndarray):
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
        if vbo_name == "indices":
            return self.ctx.buffer(vbo_data.astype(data_type).tobytes())

        return self.ctx.buffer(vbo_data.astype(data_type).tobytes())

    def create_vao(self, shader_program_name: str, shader_program: moderngl.Program):

        # Each vbo has its own configuration, so a list must be made for all before you create each VAO
        vbo_declaration_list = []
        for vbo_name, vbo_object in self.vbos.items():
            data_size = VBO_DECLARATION_MAP[vbo_name][1]
            shader_variable = VBO_DECLARATION_MAP[vbo_name][2]
            vbo_declaration_list.append((vbo_object, data_size, shader_variable))

        # Create VAOs - one per shader program
        # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
        if self.vbos.get("indices", None) is None:
            self.vaos[shader_program_name] = self.ctx.vertex_array(shader_program, vbo_declaration_list)
        else:
            self.vaos[shader_program_name] = self.ctx.vertex_array(shader_program, vbo_declaration_list, self.vbos["indices"])

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        for _, vbo in self.vbos:
            vbo.release()
