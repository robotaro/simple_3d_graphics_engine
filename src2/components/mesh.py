import numpy as np
from src.core import constants

from src.math import mat4
from src2.components.component import Component


class Mesh(Component):

    __slots__ = [
        "vertices",
        "normals",
        "colors",
        "joints",
        "weights",
        "uvs",
        "indices",
        "vaos",
        "vbo_vertices",
        "vbo_normals",
        "vbo_colors",
        "vbo_joints",
        "vbo_weights",
        "vbo_uvs",
        "ibo_indices",
        "render_mode",
        "layer",
        "visible",
        "exclusive_to_camera_uid"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # RAM Vertex data
        self.vertices = None
        self.normals = None
        self.colors = None
        self.joints = None
        self.weights = None
        self.uvs = None
        self.indices = None

        # GPU (VRAM) Vertex Data
        self.vaos = {}
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_colors = None
        self.vbo_joints = None
        self.vbo_weights = None
        self.vbo_uvs = None
        self.ibo_indices = None

        self.render_mode = self.params.get("render_mode", constants.MESH_RENDER_MODE_TRIANGLES)
        self.layer = self.params.get("layer", constants.RENDER_SYSTEM_LAYER_DEFAULT)
        self.visible = self.params.get("visible", True)

        self.exclusive_to_camera_uid = None

    def initialise(self, **kwargs):

        if self.initialised:
            return

        self.create_mesh(data_manager=kwargs[constants.MODULE_NAME_DATA_MANAGER])

        ctx = kwargs["ctx"]
        shader_library = kwargs["shader_library"]
        vbo_declaration_list = []

        # Create VBOs
        if self.vertices is not None:
            self.vbo_vertices = ctx.buffer(self.vertices.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_vertices, "3f", constants.SHADER_INPUT_VERTEX))

        if self.normals is not None:
            self.vbo_normals = ctx.buffer(self.normals.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_normals, "3f", constants.SHADER_INPUT_NORMAL))

        if self.colors is not None:
            self.vbo_colors = ctx.buffer(self.colors.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_colors, "3f", constants.SHADER_INPUT_COLOR))

        if self.joints is not None:
            self.vbo_joints = ctx.buffer(self.joints.astype("i4").tobytes())
            vbo_declaration_list.append((self.vbo_joints, "4i", constants.SHADER_INPUT_JOINT))

        if self.weights is not None:
            self.vbo_weights = ctx.buffer(self.weights.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_weights, "4f", constants.SHADER_INPUT_WEIGHT))

        if self.uvs is not None:
            self.vbo_uvs = ctx.buffer(self.uvs.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_uvs, "2f", constants.SHADER_INPUT_UV))

        if self.indices is not None:
            self.ibo_indices = ctx.buffer(self.indices.astype("i4").tobytes())

        # Create VAOs
        for program_name in constants.SHADER_PASSES_LIST:

            program = shader_library[program_name]

            # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
            if self.ibo_indices is None:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_declaration_list)
            else:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_declaration_list, self.ibo_indices)

        self.initialised = True

    def render(self, shader_pass_name: str, num_instances=1):
        self.vaos[shader_pass_name].render(mode=self.render_mode, instances=num_instances)

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.vbo_colors:
            self.vbo_colors.release()

        if self.vbo_joints:
            self.vbo_joints.release()

        if self.vbo_weights:
            self.vbo_weights.release()

        if self.vbo_uvs:
            self.vbo_uvs.release()

        if self.ibo_indices:
            self.ibo_indices.release()

    def upload_vertices(self, vertices: np.ndarray):
        self.vbo_vertices.write(vertices.tobytes())

    def upload_normals(self, normals: np.ndarray):
        self.vbo_vertices.write(normals.tobytes())

    def upload_colors(self, colors: np.ndarray):
        self.vbo_vertices.write(colors.tobytes())

    def create_mesh(self, data_manager) -> None:

        shape = self.parameters.get(constants.COMPONENT_ARG_MESH_SHAPE, None)
        resource_id = self.parameters.get(constants.COMPONENT_ARG_RESOURCE_ID, None)

        if shape is not None and resource_id is not None:
            raise KeyError("Both shape and resource ID have been specified! You either specify the shape or the mesh.")

        # Load an existing mesh file
        if resource_id is not None:
            data_group = data_manager.data_groups[resource_id]
            self.vertices = data_group.data_blocks["vertices"].data
            if "normals" in data_group.data_blocks:
                self.normals = data_group.data_blocks["normals"].data
            if "colors" in data_group.data_blocks:
                self.colors = data_group.data_blocks["colors"].data
            if "joints" in data_group.data_blocks:
                self.joints = data_group.data_blocks["joints"].data
            if "weights" in data_group.data_blocks:
                self.weights = data_group.data_blocks["weights"].data
            if "indices" in data_group.data_blocks:
                self.indices = data_group.data_blocks["indices"].data
            return

        if shape is None:
            raise Exception("[ERROR] Both resource_id and shape specification are None. Please provide one.")

        mesh_factory = MeshFactory3D()

        if shape == constants.MESH_SHAPE_BOX:
            width = Component.dict2float(input_dict=self.parameters, key="width", default_value=1.0)
            height = Component.dict2float(input_dict=self.parameters, key="height", default_value=1.0)
            depth = Component.dict2float(input_dict=self.parameters, key="depth", default_value=1.0)

            mesh = mesh_factory.create_box(width=width, height=height, depth=depth)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_ICOSPHERE:
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.5)
            subdivisions = Component.dict2int(input_dict=self.parameters, key="subdivisions", default_value=3)

            mesh = mesh_factory.create_icosphere(radius=radius, subdivisions=subdivisions)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_CAPSULE:
            height = Component.dict2float(input_dict=self.parameters, key="height", default_value=1.0)
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.25)
            count = Component.dict2tuple_int(input_dict=self.parameters, key="count", default_value=(16, 16))

            mesh = mesh_factory.create_capsule(height=height, radius=radius, count=count)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

        if shape == constants.MESH_SHAPE_CYLINDER:
            point_a = Component.dict2tuple_float(input_dict=self.parameters,
                                                 key="point_a",
                                                 default_value=(0.0, 0.0, 0.0))
            point_b = Component.dict2tuple_float(input_dict=self.parameters,
                                                 key="point_b",
                                                 default_value=(0.0, 1.0, 0.0))
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.5)
            sections = Component.dict2int(input_dict=self.parameters, key="sections", default_value=32)

            mesh = mesh_factory.create_cylinder(point_a=point_a, point_b=point_b, sections=sections, radius=radius)
            self.vertices = mesh[0]
            self.normals = mesh[1]
            self.indices = mesh[3]
            return

