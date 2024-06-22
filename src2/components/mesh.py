import numpy as np
from src.core import constants

from src2.core import meshes_3d
from src.core.data_group import DataGroup
from src2.components.component import Component


class Mesh(Component):

    __slots__ = [
        "data_blocks",
        "vaos",
        "vbos",
        "render_mode",
        "resource_id",
        "shape",
        "visible"]

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # GPU (VRAM) Vertex Data
        self.vaos = {}
        self.vbos = {}

        # Get parameters
        self.resource_id = self.params.get("resource_id", None)
        self.render_mode = self.params.get("render_mode", constants.MESH_RENDER_MODE_TRIANGLES)
        self.shape = self.params.get(constants.COMPONENT_ARG_MESH_SHAPE, None)

        # Create vbos and vaos based on mesh specifications
        if self.resource_id is not None:
            data_group = self.data_manager.data_groups.get(self.resource_id, None)
            mesh_data = self.create_from_datagroup(datagroup=data_group)

        elif self.shape is not None:
            mesh_data = self.create_from_shape(shape=self.shape, params=self.params)

        else:
            raise Exception("[ERROR] Neither 'resource_id' or 'shape' specified. You need to specify one.")

        self.create_vbo_and_vaos(mesh_data=mesh_data,
                                 shader_program_names=constants.SHADER_PASSES_LIST)

    def render(self, shader_pass_name: str, num_instances=1):
        self.vaos[shader_pass_name].render(mode=self.render_mode, instances=num_instances)

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        for _, vbo in self.vbos:
            vbo.release()

    def upload_buffer_data(self, buffer_name: str, data: np.ndarray):
        self.vbos[buffer_name].write(data.tobytes())

    def create_from_datagroup(self, datagroup: DataGroup) -> dict:

        mesh_data = {}
        meta = datagroup.metadata
        for datablock_name, datablock in datagroup.data_blocks.items():

            data = datablock.data
            if datablock_name == "indices":
                if "render_mode" in meta and meta["render_mode"] == "triangles":
                    data = np.reshape(data, (-1, 3))

            mesh_data[datablock_name] = data

        return mesh_data

    def create_from_shape(self, shape: str, params: dict) -> dict:

        if shape is None:
            raise Exception("[ERROR] Both resource_id and shape specification are None. Please provide one.")

        return meshes_3d.create_mesh(shape=shape, params=params)

    def create_vbo_and_vaos(self, mesh_data: dict, shader_program_names: list):

        vbo_declaration_list = []
        for vbo_name, vbo_data in mesh_data.items():

            data_type = Mesh.VBO_DECLARATION_MAP[vbo_name][0]
            if vbo_name == "indices":
                self.vbos[vbo_name] = self.ctx.buffer(vbo_data.astype(data_type).tobytes())
                continue

            self.vbos[vbo_name] = self.ctx.buffer(vbo_data.astype(data_type).tobytes())
            data_size = Mesh.VBO_DECLARATION_MAP[vbo_name][1]
            shader_variable = Mesh.VBO_DECLARATION_MAP[vbo_name][2]
            vbo_declaration_list.append((self.vbos[vbo_name], data_size, shader_variable))

        # Create VAOs
        for program_name in shader_program_names:

            program = self.shader_library[program_name]

            # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
            if self.vbos["indices"] is None:
                self.vaos[program_name] = self.ctx.vertex_array(program, vbo_declaration_list)
            else:
                self.vaos[program_name] = self.ctx.vertex_array(program, vbo_declaration_list, self.vbos["indices"])
