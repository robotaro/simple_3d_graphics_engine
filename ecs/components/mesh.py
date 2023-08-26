import moderngl
from typing import Union

from ecs import constants
from ecs.components.component import Component
from ecs.systems.render_system.mesh_factory import MeshFactory


class Mesh(Component):
    
    _type = constants.COMPONENT_TYPE_MESH

    __slots__ = [
        "vertices",
        "normals",
        "colors",
        "uvs",
        "faces",
        "vbo_vertices",
        "vbo_normals",
        "vbo_colors",
        "vbo_uvs",
        "ibo_faces",
        "vbo_declaration_list",
        "_gpu_initialised"
    ]

    def __init__(self, **kwargs):

        super().__init__()

        # RAM Vertex data
        self.vertices = None
        self.normals = None
        self.colors = None
        self.uvs = None
        self.faces = None

        # GPU (VRAM) Vertex Data
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_colors = None
        self.vbo_uvs = None
        self.ibo_faces = None

        # Generate external data
        shape = kwargs.get(constants.COMPONENT_ARG_MESH_SHAPE, None)
        fpath = kwargs.get(constants.COMPONENT_ARG_MESH_FPATH, None)
        self.generate_shape(shape=shape, fpath=fpath)
        self.vbo_declaration_list = []

        self._gpu_initialised = False

    def initialise_on_gpu(self, ctx: moderngl.Context) -> None:
        """
        Creates VBOs AND upload any already populated vertex arrays
        :param ctx:
        :return:
        """

        if self._gpu_initialised:
            return

        if self.vertices is not None:
            self.vbo_vertices = ctx.buffer(self.vertices.astype("f4").tobytes())
            self.vbo_declaration_list.append((self.vbo_vertices, "3f", constants.SHADER_INPUT_VERTEX))

        if self.normals is not None:
            self.vbo_normals = ctx.buffer(self.normals.astype("f4").tobytes())
            self.vbo_declaration_list.append((self.vbo_normals, "3f", constants.SHADER_INPUT_NORMAL))

        if self.colors is not None:
            self.vbo_colors = ctx.buffer(self.colors.astype("f4").tobytes())
            self.vbo_declaration_list.append((self.vbo_colors, "3f", constants.SHADER_INPUT_COLOR))

        if self.uvs is not None:
            self.vbo_uvs = ctx.buffer(self.colors.astype("f4").tobytes())
            self.vbo_declaration_list.append((self.vbo_uvs, "2f", constants.SHADER_INPUT_UV))

        if self.faces is not None:
            self.ibo_faces = ctx.buffer(self.faces.astype("i4").tobytes())

        self._gpu_initialised = True

    def upload_buffers(self) -> None:

        """
        Uploades current vertices referenced externally (in RAM) to the GPU
        :return:
        """

        if not self._gpu_initialised:
            return

        if self.vbo_vertices is not None:
            self.vbo_vertices.write(self.vertices.tobytes())

        if self.vbo_normals is not None:
            self.vbo_normals.write(self.normals.tobytes())

        if self.vbo_colors is not None:
            self.vbo_colors.write(self.colors.tobytes())

        if self.vbo_uvs is not None:
            self.vbo_uvs.write(self.normals.tobytes())

        # TODO: Consider the case where the number of vertices changes and so the number of faces

    def get_vbo_declaration_list(self) -> list:

        if not self._gpu_initialised:
            return None

        return self.vbo_declaration_list

    def release(self):
        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.vbo_uvs:
            self.vbo_uvs.release()

        if self.ibo_faces:
            self.ibo_faces.release()

    def generate_shape(self, shape: Union[str, None] = None, **kwargs) -> None:

        if shape is None:
            return

        # To avoid warnings
        v, n, u, f = None, None, None, None

        if shape == constants.MESH_SHAPE_CUBE:
            raise NotImplemented(f"[ERROR] Shape {constants.MESH_SHAPE_CUBE} not yet implement")

        if shape == constants.MESH_SHAPE_SPHERE:
            raise NotImplemented(f"[ERROR] Shape {constants.MESH_SHAPE_SPHERE} not yet implement")

        if shape == constants.MESH_SHAPE_CYLINDER:
            raise NotImplemented(f"[ERROR] Shape {constants.MESH_SHAPE_CYLINDER} not yet implement")

        if shape == constants.MESH_SHAPE_FROM_OBJ:
            if "fpath" not in kwargs:
                raise KeyError("[ERROR] Missing argument 'fpath' in order to load OBJ file")
            v, n, u, f = MeshFactory.from_obj(fpath=kwargs["fpath"])

        self.vertices = v
        self.normals = n
        self.uvs = u
        self.faces = f


