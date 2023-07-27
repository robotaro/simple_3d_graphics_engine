
import numpy as np
import trimesh
import moderngl
from core.material import Material

from core.node import Node


class Mesh(Node):

    _type = "mesh"

    def __init__(self,
                 vertices=None,
                 normals=None,
                 uvs=None,
                 faces=None,
                 material=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actual data stored here
        self.vertices = None    # nd.array (N, 3) <float32>
        self.normals = None     # nd.array (N, 3) <float32>
        self.faces = None       # nd.array (N, 3) <uint32>
        self.uvs = None         # nd.array (N, 2) <float32>

        # Materials
        self.alpha = 1.0
        self.material = material

        # VBOs and VAO
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_colors = None
        self.vbo_indices = None
        self.vbo_uvs = None
        self.vao = None

        # Flags
        self._vbo_dirty_flag = True
        self._instanced = False
        self.is_renderable = True

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
        return False

    def release(self):
        if self.vbo_vertices:
            self.vbo_vertices.release()

        if self.vbo_normals:
            self.vbo_normals.release()

        if self.vbo_colors:
            self.vbo_colors.release()

        if self.vbo_indices:
            self.vbo_indices.release()

        if self.vbo_uvs:
            self.vbo_uvs.release()

        if self.vao:
            self.vao.release()


    # =========================================================================
    #                   Rendering and GPU upload functions
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

        if self._vbo_dirty_flag:
            self._upload_buffers()
            self._vbo_dirty_flag = False

        if self.vao:
            prog = self._use_program(kwargs["camera"], **kwargs)
            self.vao.render(prog, moderngl.TRIANGLES, instances=self.n_instances)

    def _upload_buffers(self):

        # Write positions.
        self.vbo_vertices.write(self.current_vertices.astype("f4").tobytes())

        # Write normals.
        if not self.flat_shading:
            vertex_normals = self.vertex_normals_at(self.current_frame_id)
            self.vbo_normals.write(vertex_normals.astype("f4").tobytes())

        if self.face_colors is None:
            # Write vertex colors.
            self.vbo_colors.write(self.current_vertex_colors.astype("f4").tobytes())
        else:
            # Write face colors.

            # Compute shape of 2D texture.
            shape = (min(self.faces.shape[0], 8192), (self.faces.shape[0] + 8191) // 8192)

            # Write texture left justifying the buffer to fill the last row of the texture.
            self.face_colors_texture.write(
                self.current_face_colors.astype("f4").tobytes().ljust(shape[0] * shape[1] * 16)
            )

        # Write uvs.
        if self.has_texture:
            self.vbo_uvs.write(self.uv_coords.astype("f4").tobytes())

        # Write instance transforms.
        if self.instance_transforms is not None:
            self.vbo_instance_transforms.write(
                np.transpose(self.current_instance_transforms.astype("f4"), (0, 2, 1)).tobytes()
            )

    def _use_program(self, camera, **kwargs):

        if self.has_texture and self.show_texture:
            prog = self.texture_prog
            prog["diffuse_texture"] = 0
            self.texture.use(0)
        else:
            if self.face_colors is None:
                if self.flat_shading:
                    prog = self.flat_prog
                else:
                    prog = self.smooth_prog
            else:
                if self.flat_shading:
                    prog = self.flat_face_prog
                else:
                    prog = self.smooth_face_prog
                self.face_colors_texture.use(0)
                prog["face_colors"] = 0
            prog["norm_coloring"].value = self.norm_coloring

        prog["use_uniform_color"] = self._use_uniform_color
        prog["uniform_color"] = self.material.color
        prog["draw_edges"].value = 1.0 if self.draw_edges else 0.0
        prog["win_size"].value = kwargs["window_size"]

        prog["clip_control"].value = tuple(self.clip_control)
        prog["clip_value"].value = tuple(self.clip_value)

        self.set_camera_matrices(prog, camera, **kwargs)
        set_lights_in_program(
            prog,
            kwargs["lights"],
            kwargs["shadows_enabled"],
            kwargs["ambient_strength"],
        )
        set_material_properties(prog, self.material)
        self.receive_shadow(prog, **kwargs)
        return prog


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

