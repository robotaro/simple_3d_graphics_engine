from ecs import constants
from ecs.components.component import Component
from ecs.utilities import utils_mesh_3d


class Mesh(Component):
    
    _type = constants.COMPONENT_TYPE_MESH

    __slots__ = [
        "vertices",
        "normals",
        "colors",
        "uvs",
        "faces",
        "vaos",
        "vbo_vertices",
        "vbo_normals",
        "vbo_colors",
        "vbo_uvs",
        "ibo_faces",
        "visible"
    ]

    def __init__(self, parameters: dict):

        super().__init__(parameters=parameters)

        # RAM Vertex data
        self.vertices = None
        self.normals = None
        self.colors = None
        self.uvs = None
        self.faces = None

        # GPU (VRAM) Vertex Data
        self.vaos = {}
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_colors = None
        self.vbo_uvs = None
        self.ibo_faces = None

        self.generate_shape()

        # Flags
        self.visible = True
        
    def initialise(self, **kwargs):

        if self.initialised:
            return

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

        if self.uvs is not None:
            self.vbo_uvs = ctx.buffer(self.uvs.astype("f4").tobytes())
            vbo_declaration_list.append((self.vbo_uvs, "2f", constants.SHADER_INPUT_UV))

        if self.faces is not None:
            self.ibo_faces = ctx.buffer(self.faces.astype("i4").tobytes())

        # Create VAOs
        for program_name in constants.SHADER_PASSES_LIST:

            program = shader_library[program_name]

            # TODO: I think one version serves both if ibo_faces is None. Default value seems ot be None as well
            if self.ibo_faces is None:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_declaration_list)
            else:
                self.vaos[program_name] = ctx.vertex_array(program, vbo_declaration_list, self.ibo_faces)

        self.initialised = True

    def release(self):

        for _, vao in self.vaos:
            vao.release()

        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.vbo_uvs:
            self.vbo_uvs.release()

        if self.ibo_faces:
            self.ibo_faces.release()

    """def upload_buffers(self) -> None:
    
        # Not being used yet

        if not self.initialised:
            return

        if self.vbo_vertices is not None:
            self.vbo_vertices.write(self.vertices.tobytes())

        if self.vbo_normals is not None:
            self.vbo_normals.write(self.normals.tobytes())

        if self.vbo_colors is not None:
            self.vbo_colors.write(self.colors.tobytes())

        if self.vbo_uvs is not None:
            self.vbo_uvs.write(self.normals.tobytes())

        # TODO: Consider the case where the number of vertices changes and so the number of faces"""

    def generate_shape(self) -> None:

        shape = self.parameters.get(constants.COMPONENT_ARG_MESH_SHAPE, None)
        if shape is None:
            return

        # To avoid warnings
        v, n, u, f = None, None, None, None

        if shape == constants.MESH_SHAPE_BOX:
            width = Component.dict2float(input_dict=self.parameters, key="width", default_value=1.0)
            height = Component.dict2float(input_dict=self.parameters, key="height", default_value=1.0)
            depth = Component.dict2float(input_dict=self.parameters, key="depth", default_value=1.0)
            v, n, u, f = utils_mesh_3d.create_box(width=width, height=height, depth=depth)

        if shape == constants.MESH_SHAPE_ICOSPHERE:
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.5)
            subdivisions = Component.dict2int(input_dict=self.parameters, key="subdivisions", default_value=3)
            v, n, u, f = utils_mesh_3d.create_icosphere(radius=radius, subdivisions=subdivisions)

        if shape == constants.MESH_SHAPE_CAPSULE:
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.5)
            subdivisions = Component.dict2int(input_dict=self.parameters, key="subdivisions", default_value=3)
            v, n, u, f = utils_mesh_3d.create_icosphere(radius=radius, subdivisions=subdivisions)

        if shape == constants.MESH_SHAPE_CYLINDER:
            point_a = Component.dict2tuple_float(input_dict=self.parameters,
                                                 key="point_a",
                                                 default_value=(0.0, 0.0, 0.0))
            point_b = Component.dict2tuple_float(input_dict=self.parameters,
                                                 key="point_a",
                                                 default_value=(0.0, 1.0, 0.0))
            radius = Component.dict2float(input_dict=self.parameters, key="radius", default_value=0.5)
            sections = Component.dict2int(input_dict=self.parameters, key="sections", default_value=32)

            v, n, u, f = utils_mesh_3d.create_cylinder(point_a=point_a, point_b=point_b,
                                                       sections=sections, radius=radius)

        if shape == constants.MESH_SHAPE_FROM_OBJ:
            fpath = self.parameters.get(constants.COMPONENT_ARG_MESH_FPATH, None)
            if fpath is None:
                raise KeyError("[ERROR] Missing argument 'fpath' in order to load OBJ file")
            v, n, u, f = utils_mesh_3d.from_obj(fpath=self.parameters["fpath"])

        self.vertices = v
        self.normals = n
        self.uvs = u
        self.faces = f
