import moderngl

from ecs import constants
from ecs.components.component import Component


class Mesh(Component):
    
    _type = constants.COMPONENT_TYPE_MESH

    __slots__ = [
        "vertices",
        "normals",
        "colors",
        "faces",
        "vbo_vertices",
        "vbo_normals",
        "vbo_colors",
        "ibo_faces"
    ]

    def __init__(self):

        self.vertices = None
        self.normals = None
        self.colors = None
        self.faces = None

        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_colors = None
        self.ibo_faces = None

        self._gpu_initialised = False

    def initialise_on_gpu(self, ctx: moderngl.Context):

        if self._gpu_initialised:
            return

        if self.vertices is not None:
            self.vbo_vertices = ctx.buffer(self.vertices.astype("f4").tobytes())

        if self.normals is not None:
            self.vbo_normals = ctx.buffer(self.normals.astype("f4").tobytes())

        if self.colors is not None:
            self.vbo_colors = ctx.buffer(self.colors.astype("f4").tobytes())

        if self.faces is not None:
            self.ibo_faces = ctx.buffer(self.faces.astype("i4").tobytes())

        self._gpu_initialised = True

    def upload_buffers(self):

        if not self._gpu_initialised:
            return

        if self.vbo_vertices is not None:
            self.vbo_vertices.write(self.vertices.astype("f4").tobytes())

        if self.vbo_normals is not None:
            self.vbo_normals.write(self.normals.astype("f4").tobytes())

        if self.vbo_colors is not None:
            self.vbo_colors.write(self.colors.astype("f4").tobytes())

        # TODO: COnside the case where the number of vertices changes and so the number of faces

    def get_vbo_tuple_list(self) -> list:

        if not self._gpu_initialised:
            return None

        return [
            (self.vbo_vertices, "3f", "in_vert"),
            (self.vbo_normals, "3f", "in_vert"),
            (self.vbo_vertices, "3f", "in_vert"),
        ]

    def release(self):
        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.ibo_faces:
            self.ibo_faces.release()