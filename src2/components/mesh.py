import numpy as np
from src.core import constants

from src.geometry_3d.mesh_factory_3d import MeshFactory3D
from src2.components.component import Component


class Mesh(Component):

    __slots__ = [
        "vaos",
        "vbos",
        "ibo_indices",
        "render_mode",
        "resource_id",
        "layer",
        "visible"]

    VBO_DECLARATION_MAP = {
        #           (buffer_data_type, buffer_data_size, shader_variable)
        "vertices": ("f4", "3f", constants.SHADER_INPUT_VERTEX),
        "normals": ("f4", "3f", constants.SHADER_INPUT_NORMAL),
        "colors": ("f4", "3f", constants.SHADER_INPUT_COLOR),
        "joints": ("i4", "4i", constants.SHADER_INPUT_JOINT),
        "weights": ("f4", "4f", constants.SHADER_INPUT_WEIGHT),
        "uvs": ("f4", "2f", constants.SHADER_INPUT_UV),
        "indices": ("i4", None, constants.SHADER_INPUT_UV),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # GPU (VRAM) Vertex Data
        self.vaos = {}
        self.vbos = {}
        self.ibo_indices = None

        # Get parameters
        self.resource_id = self.params.get("resource_id", None)
        self.render_mode = self.params.get("render_mode", constants.MESH_RENDER_MODE_TRIANGLES)

        #self.create_mesh()


        data_group = self.data_manager.data_groups.get(self.resource_id, None)
        if data_group is None:
            return

        # Generate all VBO declarations for each VAO that will create in the next stage
        vbo_declaration_list = []
        for data_block_name, data_block in data_group.data_blocks.items():

            data_type = Mesh.VBO_DECLARATION_MAP[data_block_name][0]
            if data_block_name == "indices":
                self.ibo_indices = self.ctx.buffer(data_block.data.astype(data_type).tobytes())
                continue

            self.vbos[data_block_name] = self.ctx.buffer(data_block.data.astype(data_type).tobytes())
            data_size = Mesh.VBO_DECLARATION_MAP[data_block_name][1]
            shader_variable = Mesh.VBO_DECLARATION_MAP[data_block_name][2]
            vbo_declaration_list.append((self.vbos[data_block_name], data_size, shader_variable))

        # Create VAOs
        for program_name in constants.SHADER_PASSES_LIST:

            program = self.shader_library[program_name]

            # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
            if self.ibo_indices is None:
                self.vaos[program_name] = self.ctx.vertex_array(program, vbo_declaration_list)
            else:
                self.vaos[program_name] = self.ctx.vertex_array(program, vbo_declaration_list, self.ibo_indices)

    def render(self, shader_pass_name: str, num_instances=1):
        self.vaos[shader_pass_name].render(mode=self.render_mode, instances=num_instances)

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        for _, vbo in self.vbos:
            vbo.release()

        if self.ibo_indices:
            self.ibo_indices.release()

    def upload_buffer_data(self, buffer_name: str, data: np.ndarray):
        self.vbos[buffer_name].write(data.tobytes())

    def create_mesh(self) -> None:

        shape = self.params.get(constants.COMPONENT_ARG_MESH_SHAPE, None)

        if shape is None:
            raise Exception("[ERROR] Both resource_id and shape specification are None. Please provide one.")

        mesh_factory = MeshFactory3D()

        if shape == constants.MESH_SHAPE_BOX:
            width = self.params.get("width", 1.0)
            height = self.params.get("height", 1.0)
            depth = self.params.get("depth", 1.0)

            mesh = mesh_factory.create_box(width=width, height=height, depth=depth)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_ICOSPHERE:
            radius = self.params.get("radius", 0.5)
            subdivisions = self.params.get("subdivisions", 3)

            mesh = mesh_factory.create_icosphere(radius=radius, subdivisions=subdivisions)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_CAPSULE:
            height = self.params.get("height", 1.0)
            radius = self.params.get("radius", 0.25)
            count = self.params.get("count", (16, 16))

            mesh = mesh_factory.create_capsule(height=height, radius=radius, count=count)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_CYLINDER:
            point_a = self.params.get("point_a", (0.0, 0.0, 0.0))
            point_b = self.params.get("point_b", (0.0, 1.0, 0.0))
            radius = self.params.get("radius", 0.5)
            sections = self.params.get("sections", 32)

            mesh = mesh_factory.create_cylinder(point_a=point_a, point_b=point_b, sections=sections, radius=radius)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return
