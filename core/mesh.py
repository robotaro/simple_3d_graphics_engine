
import numpy as np
import trimesh
import moderngl

from core.node import Node


class Mesh(Node):

    _type = "mesh"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actual data stored here
        self.vertices = None
        self.normals = None
        self.indices = None

        # Rendering variables
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_indices = None
        self.vbo_uvs = None
        self.vao = None

        self._bounds = None

    @property
    def bounds(self):
        """(2,3) float : The axis-aligned bounds of the mesh.
        """
        if self._bounds is None:
            bounds = np.array([[np.infty, np.infty, np.infty],
                               [-np.infty, -np.infty, -np.infty]])
            for p in self.primitives:
                bounds[0] = np.minimum(bounds[0], p.bounds[0])
                bounds[1] = np.maximum(bounds[1], p.bounds[1])
            self._bounds = bounds
        return self._bounds

    @property
    def centroid(self):
        """(3,) float : The centroid of the mesh's axis-aligned bounding box
        (AABB).
        """
        return np.mean(self.bounds, axis=0)

    @property
    def extents(self):
        """(3,) float : The lengths of the axes of the mesh's AABB.
        """
        return np.diff(self.bounds, axis=0).reshape(-1)

    @property
    def is_transparent(self):
        for p in self.primitives:
            if p.is_transparent:
                return True
        return False

    def release(self):
        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_uvs:
            self.vbo_uvs.release()

        if self.vbo_indices:
            self.vbo_indices.release()

        if self.vao:
            self.vao.release()


    # =========================================================================
    #                          Rendering functions
    # =========================================================================

    @Node.once
    def make_renderable(self, ctx: moderngl.Context, program: moderngl.Program):

        self.vbo_vertices = ctx.buffer(self.vertices.astype("f4").tobytes())
        self.vbo_indices = ctx.buffer(self.faces.astype("i4").tobytes())

        self.vao = ctx.vertex_array(
            program,
            [
                (self.vbo_vertices, "3f4", "in_position"),
                (self.vbo_uvs, "3f4", "in_normals"),
                (self.vbo_uvs, "2f4", "in_uvs"),
            ],
        )

    def render(self, **kwargs):
        if self.vao:
            self.vao.render(moderngl.TRIANGLES)

    # =========================================================================
    #                           Mesh Generation
    # =========================================================================

    @staticmethod
    def from_points(points, colors=None, normals=None,
                    is_visible=True, poses=None):
        """Create a Mesh from a set of points.

        Parameters
        ----------
        points : (n,3) float
            The point positions.
        colors : (n,3) or (n,4) float, optional
            RGB or RGBA colors for each point.
        normals : (n,3) float, optionals
            The normal vectors for each point.
        is_visible : bool
            If False, the points will not be rendered.
        poses : (x,4,4)
            Array of 4x4 transformation matrices for instancing this object.

        Returns
        -------
        mesh : :class:`Mesh`
            The created mesh.
        """
        primitive = Primitive(
            positions=points,
            normals=normals,
            color_0=colors,
            mode=GLTF.POINTS,
            poses=poses
        )
        mesh = Mesh(primitives=[primitive], is_visible=is_visible)
        return mesh

