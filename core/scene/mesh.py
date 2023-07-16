import os
import pickle
import re
from functools import lru_cache

import moderngl
import numpy as np
import tqdm
import trimesh
import trimesh.geometry
from moderngl_window.opengl.vao import VAO
from PIL import Image
from trimesh.triangles import points_to_barycentric

from aitviewer.scene.node import Node
from aitviewer.shaders import (
    get_depth_only_program,
    get_flat_lit_with_edges_face_color_program,
    get_flat_lit_with_edges_program,
    get_fragmap_program,
    get_outline_program,
    get_smooth_lit_texturized_program,
    get_smooth_lit_with_edges_face_color_program,
    get_smooth_lit_with_edges_program,
)
from aitviewer.utils import set_lights_in_program, set_material_properties
from aitviewer.utils.decorators import hooked
from aitviewer.utils.so3 import euler2rot_numpy, rot2euler_numpy
from aitviewer.utils.utils import compute_vertex_and_face_normals_sparse


class Meshes(Node):
    """A sequence of triangle meshes. This assumes that the mesh topology is fixed over the sequence."""

    def __init__(
        self,
        vertices,
        faces,
        vertex_normals=None,
        face_normals=None,
        vertex_colors=None,
        face_colors=None,
        uv_coords=None,
        path_to_texture=None,
        cast_shadow=True,
        pickable=True,
        flat_shading=False,
        draw_edges=False,
        draw_outline=False,
        instance_transforms=None,
        icon="\u008d",
        **kwargs,
    ):
        """
        Initializer.
        :param vertices: A np array of shape (N, V, 3) or (V, 3).
        :param faces: A np array of shape (F, 3).
        :param vertex_normals: A np array of shape (N, V, 3). If not provided, the vertex normals will be computed,
          which incurs some overhead.
        :param face_normals: A np array of shape (N, F, 3). If not provided, the face normals will be computed, which
          incurs some overhead.
        :param vertex_colors: A np array of shape (N, V, 4) overriding the uniform color.
        :param face_colors: A np array of shape (N, F, 4) overriding the uniform or vertex colors.
        :param uv_coords: A np array of shape (V, 2) if the mesh is to be textured.
        :param path_to_texture: Path to an image file that serves as the texture.
        :param cast_shadow: If True the mesh casts a shadow on other objects.
        :param pickable: If True the mesh can be selected with a mouse click.
        :param flat_shading: If True the each face of the mesh is shaded with a constant normal.
        :param draw_edges: If True the normals the edges of the mesh is drawn on top of the mesh.
        :param draw_outline: If true an outline is drawn around the mesh.
        :instance_transforms: np array of size (N, I, 4, 4) or (I, 4, 4) or None. If not None, 'I' instances of
            the same mesh will be rendered, each with its own transformation matrix.
        """
        if len(vertices.shape) == 2 and vertices.shape[-1] == 3:
            vertices = vertices[np.newaxis]
        assert len(vertices.shape) == 3
        assert len(faces.shape) == 2
        n_frames = vertices.shape[0]

        # Instancing.
        if instance_transforms is not None:
            # Check shape of transforms.
            if len(instance_transforms.shape) == 3:
                instance_transforms = instance_transforms[np.newaxis]
            assert len(instance_transforms.shape) == 4

            # Number of instance frames must match number of frames or be 1.
            assert n_frames == 1 or instance_transforms.shape[0] == 1 or n_frames == instance_transforms.shape[0]
            n_frames = max(n_frames, instance_transforms.shape[0])

            self._instance_transforms = instance_transforms
        else:
            self._instance_transforms = None

        super(Meshes, self).__init__(n_frames=n_frames, icon=icon, **kwargs)

        self._vertices = vertices
        self._faces = faces.astype(np.int32)

        # Create these first because other setters can call redraw() which uses this fields.
        self._face_colors = None
        self._vertex_colors = None
        self._has_transparent_vertex_or_face_colors = False

        def _maybe_unsqueeze(x):
            return x[np.newaxis] if x is not None and x.ndim == 2 else x

        self._vertex_normals = _maybe_unsqueeze(vertex_normals)
        self._face_normals = _maybe_unsqueeze(face_normals)
        self.vertex_colors = _maybe_unsqueeze(vertex_colors)
        self.face_colors = _maybe_unsqueeze(face_colors)

        # Texture handling.
        self.has_texture = uv_coords is not None
        self.uv_coords = uv_coords

        if self.has_texture:
            self.use_pickle_texture = path_to_texture.endswith((".pickle", "pkl"))
            if self.use_pickle_texture:
                self.texture_image = pickle.load(open(path_to_texture, "rb"))
            else:
                self.texture_image = Image.open(path_to_texture).transpose(method=Image.FLIP_TOP_BOTTOM).convert("RGB")
        else:
            self.texture_image = None

        # Enable rendering passes
        self.cast_shadow = cast_shadow
        self.fragmap = pickable
        self.depth_prepass = True
        self.outline = True

        # Misc.
        self._flat_shading = flat_shading
        self.draw_edges = draw_edges
        self.draw_outline = draw_outline
        self.show_texture = self.has_texture
        self.norm_coloring = False
        self.normals_r = None
        self.need_upload = True
        self._use_uniform_color = self._vertex_colors is None and self._face_colors is None
        self._vertex_faces_sparse = trimesh.geometry.index_sparse(self._vertices.shape[1], self._faces)

        self.clip_control = np.array((0, 0, 0), np.int32)
        self.clip_value = np.array((0, 0, 0), np.float32)

    @classmethod
    def instanced(cls, *args, positions=None, rotations=None, scales=None, **kwargs):
        """
        Creates and returns an instanced sequence of N frames and I instances.
        Each instance will have its own position, rotation and scale.
        :param positions: np array of size (N, I, 3) or (I, 3) or None.
        :param rotations: np array of size (N, I, 3, 3) or (I, 3, 3) or None.
        :param scales: np array of size (N, I) or (I) or None.

        *args, and **kwargs are forwarded to the Meshes constructor.
        """
        assert positions is not None or rotations is not None or scales is not None

        n_instances = 0
        n_frames = 0

        def check_array(a, dim):
            nonlocal n_instances, n_frames
            if a is not None:
                if len(a.shape) == dim + 1:
                    a = a[np.newaxis]
                n_frames = max(n_frames, a.shape[0])
                n_instances = max(n_instances, a.shape[1])
            return a

        positions = check_array(positions, 1)
        rotations = check_array(rotations, 2)
        scales = check_array(scales, 0)

        if positions is None:
            positions = np.zeros((n_frames, n_instances, 3))
        if rotations is None:
            rotations = np.zeros((n_frames, n_instances, 3, 3))
            rotations[:, :] = np.eye(3)
        if scales is None:
            scales = np.ones((n_frames, n_instances))

        transforms = np.zeros((n_frames, n_instances, 4, 4))
        transforms[:, :, :3, :3] = (rotations.reshape((-1, 9)) * scales.reshape((-1, 1))).reshape(
            (n_frames, n_instances, 3, 3)
        )
        transforms[:, :, :3, 3] = positions
        transforms[:, :, 3, 3] = 1.0
        return cls(*args, **kwargs, instance_transforms=transforms)

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        if len(vertices.shape) == 2:
            vertices = vertices[np.newaxis]

        # Update vertices and redraw
        self._vertices = vertices
        self.n_frames = len(vertices)

        # If vertex or face normals were supplied, they are no longer valid.
        self._vertex_normals = None
        self._face_normals = None

        # Must clear all LRU caches where the vertices are used.
        self.compute_vertex_and_face_normals.cache_clear()

        self.redraw()

    @property
    def faces(self):
        return self._faces

    @faces.setter
    def faces(self, f):
        self._faces = f.astype(np.int32)
        self._vertex_faces_sparse = trimesh.geometry.index_sparse(self.vertices.shape[1], self._faces)

    @property
    def current_vertices(self):
        idx = self.current_frame_id if self.vertices.shape[0] > 1 else 0
        return self.vertices[idx]

    @current_vertices.setter
    def current_vertices(self, vertices):
        idx = self.current_frame_id if self.vertices.shape[0] > 1 else 0
        self._vertices[idx] = vertices
        self.compute_vertex_and_face_normals.cache_clear()
        self.redraw()

    @property
    def current_transformed_vertices(self):
        return (self.current_vertices @ self.model_matrix[:3, :3].T) + self.model_matrix[:3, 3]

    @property
    def transformed_vertices(self):
        return (self.vertices @ self.model_matrix[:3, :3].T) + self.model_matrix[:3, 3]

    @property
    def n_faces(self):
        return self.faces.shape[0]

    @property
    def n_vertices(self):
        return self.vertices.shape[1]

    @property
    def vertex_faces(self):
        # To compute the normals we need to know a mapping from vertex ID to all faces that this vertex is part of.
        # Because we are lazy we abuse trimesh to compute this for us. Not all vertices have the maximum degree, so
        # this array is padded with -1 if necessary.
        return trimesh.Trimesh(self.vertices[0], self.faces, process=False).vertex_faces

    @property
    def vertex_normals(self):
        """Get or compute all vertex normals (this might take a while for long sequences)."""
        if self._vertex_normals is None:
            vertex_normals, _ = compute_vertex_and_face_normals_sparse(
                self.vertices, self.faces, self._vertex_faces_sparse, normalize=True
            )
            self._vertex_normals = vertex_normals
        return self._vertex_normals

    @property
    def face_normals(self):
        """Get or compute all face normals (this might take a while for long sequences)."""
        if self._face_normals is None:
            _, face_normals = compute_vertex_and_face_normals_sparse(
                self.vertices, self.faces, self._vertex_faces_sparse, normalize=True
            )
            self._face_normals = face_normals
        return self._face_normals

    def vertex_normals_at(self, frame_id):
        """Get or compute the vertex normals at the given frame."""
        if self._vertex_normals is None:
            vn, _ = self.compute_vertex_and_face_normals(frame_id, normalize=True)
        else:
            assert len(self._vertex_normals.shape) == 3, f"Got shape {self._vertex_normals.shape}"
            vn = self._vertex_normals[frame_id]
        return vn

    def face_normals_at(self, frame_id):
        """Get or compute the face normals at the given frame."""
        if self._face_normals is None:
            _, fn = self.compute_vertex_and_face_normals(frame_id, normalize=True)
        else:
            assert len(self._face_normals.shape) == 3, f"Got shape {self._face_normals.shape}"
            fn = self._face_normals[frame_id]
        return fn

    @property
    def vertex_colors(self):
        if self._vertex_colors is None:
            self._vertex_colors = np.full((self.n_frames, self.n_vertices, 4), self.material.color)
        return self._vertex_colors

    @vertex_colors.setter
    def vertex_colors(self, vertex_colors):
        # If vertex_colors are None, we resort to the material color.
        if vertex_colors is None:
            self._vertex_colors = None
            self._use_uniform_color = True
        elif isinstance(vertex_colors, tuple) and len(vertex_colors) == 4:
            self.vertex_colors = None
            self._use_uniform_color = True
            self.material.color = vertex_colors
        else:
            if len(vertex_colors.shape) == 2:
                assert vertex_colors.shape[0] == self.n_vertices
                vertex_colors = np.repeat(vertex_colors[np.newaxis], self.n_frames, axis=0)
            assert len(vertex_colors.shape) == 3
            self._vertex_colors = vertex_colors
            self._use_uniform_color = False
            self.redraw()

    @property
    def current_vertex_colors(self):
        if self._use_uniform_color:
            return np.full((self.n_vertices, 4), self.material.color)
        else:
            idx = self.current_frame_id if self.vertex_colors.shape[0] > 1 else 0
            return self.vertex_colors[idx]

    @property
    def face_colors(self):
        return self._face_colors

    @face_colors.setter
    def face_colors(self, face_colors):
        if face_colors is not None:
            if len(face_colors.shape) == 2:
                face_colors = face_colors[np.newaxis]
            self._face_colors = face_colors
            self._use_uniform_color = False
        else:
            self._face_colors = None
        self.redraw()

    @property
    def current_face_colors(self):
        if self._use_uniform_color:
            return np.full((self.n_faces, 4), self.material.color)
        else:
            idx = self.current_frame_id if self.face_colors.shape[0] > 1 else 0
            return self.face_colors[idx]

    @Node.color.setter
    def color(self, color):
        self.material.color = color

        if self.face_colors is None:
            self.vertex_colors = color

    @property
    def flat_shading(self):
        return self._flat_shading

    @flat_shading.setter
    def flat_shading(self, flat_shading):
        if self._flat_shading != flat_shading:
            self._flat_shading = flat_shading
            self.redraw()

    def closest_vertex_in_triangle(self, tri_id, point):
        face_vertex_id = np.linalg.norm((self.current_vertices[self.faces[tri_id]] - point), axis=-1).argmin()
        return self.faces[tri_id][face_vertex_id]

    def get_bc_coords_from_points(self, tri_id, points):
        return points_to_barycentric(self.current_vertices[self.faces[[tri_id]]], points)[0]

    @lru_cache(2048)
    def compute_vertex_and_face_normals(self, frame_id, normalize=False):
        """
        Compute face and vertex normals for the given frame. We use an LRU cache since this is a potentially
        expensive operation. This function exists because computing the normals on all frames can increase the
        startup time of the viewer considerably.

        :param frame_id: On which frame to compute the normals.
        :param normalize: Whether or not to normalize the normals. Not doing it is faster and the shaders typically
          enforce unit length of normals anyway.
        :return: The vertex and face normals as a np arrays of shape (V, 3) and (F, 3) respectively.
        """
        vs = self.vertices[frame_id : frame_id + 1] if self.vertices.shape[0] > 1 else self.vertices
        vn, fn = compute_vertex_and_face_normals_sparse(vs, self.faces, self._vertex_faces_sparse, normalize)
        return vn.squeeze(0), fn.squeeze(0)

    @property
    def bounds(self):
        if self.instance_transforms is None:
            return self.get_bounds(self.vertices)
        else:
            # Get bounds in local coordinates
            bounds = self.get_local_bounds(self.vertices)

            # Transform bounds with instance transforms
            min = np.append(bounds[:, 0], 1.0)
            max = np.append(bounds[:, 1], 1.0)
            transforms = self.instance_transforms.reshape((-1, 4, 4))
            mins = transforms @ min
            maxs = transforms @ max

            # Return bounds in world coordinates
            return self.get_bounds(np.vstack((mins, maxs)))

    @property
    def current_bounds(self):
        if self.instance_transforms is None:
            return self.get_bounds(self.current_vertices)
        else:
            # Get bounds in local coordinates
            bounds = self.get_local_bounds(self.current_vertices)

            # Transform bounds with instance transforms
            min = np.append(bounds[:, 0], 1.0)
            max = np.append(bounds[:, 1], 1.0)
            transforms = self.current_instance_transforms.reshape((-1, 4, 4))
            mins = transforms @ min
            maxs = transforms @ max

            # Return bounds in world coordinates
            return self.get_bounds(np.vstack((mins[:, :3], maxs[:, :3])))

    def is_transparent(self):
        return self.color[3] < 1.0 or self._has_transparent_vertex_or_face_colors

    def on_frame_update(self):
        """Called whenever a new frame must be displayed."""
        super().on_frame_update()
        self.redraw()

    @property
    def current_instance_transforms(self):
        if self._instance_transforms is None:
            return None
        idx = self.current_frame_id if self._instance_transforms.shape[0] > 1 else 0
        return self._instance_transforms[idx]

    @property
    def instance_transforms(self):
        return self._instance_transforms

    @instance_transforms.setter
    def instance_transforms(self, instance_transforms):
        assert self._instance_transforms.shape == instance_transforms
        self._instance_transforms = instance_transforms

    @property
    def n_instances(self):
        if self._instance_transforms is None:
            return 1
        else:
            return self._instance_transforms.shape[1]

    def _upload_buffers(self):
        """Upload the current frame data to the GPU for rendering."""
        if not self.is_renderable or not self._need_upload:
            return

        self._need_upload = False

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

    @hooked
    def redraw(self, **kwargs):
        self._need_upload = True

        transparent = False
        if self._vertex_colors is not None:
            transparent = transparent or np.any(self.vertex_colors[:, :, 3] < 1.0)
        if self._face_colors is not None:
            transparent = transparent or np.any(self.face_colors[:, :, 3] < 1.0)

        self._has_transparent_vertex_or_face_colors = transparent

    def _load_programs(self, vs, positions_vs):
        instanced = 1 if self.instance_transforms is not None else 0
        self.smooth_prog = get_smooth_lit_with_edges_program(vs, instanced)
        self.flat_prog = get_flat_lit_with_edges_program(vs, instanced)
        self.smooth_face_prog = get_smooth_lit_with_edges_face_color_program(vs, instanced)
        self.flat_face_prog = get_flat_lit_with_edges_face_color_program(vs, instanced)

        self.depth_only_program = get_depth_only_program(positions_vs, instanced)
        self.outline_program = get_outline_program(positions_vs, instanced)
        self.fragmap_program = get_fragmap_program(positions_vs, instanced)

    # noinspection PyAttributeOutsideInit
    @Node.once
    def make_renderable(self, ctx: moderngl.Context):
        """Prepares this object for rendering. This function must be called before `render` is used."""
        vs = "lit_with_edges.glsl"
        positions_vs = "mesh_positions.vs.glsl"
        self._load_programs(vs, positions_vs)

        vertices = self.current_vertices
        vertex_normals = self.vertex_normals_at(self.current_frame_id)
        vertex_colors = self.current_vertex_colors

        self.vbo_vertices = ctx.buffer(vertices.astype("f4").tobytes())
        self.vbo_normals = ctx.buffer(vertex_normals.astype("f4").tobytes())
        self.vbo_colors = ctx.buffer(vertex_colors.astype("f4").tobytes())
        self.vbo_indices = ctx.buffer(self.faces.tobytes())

        self.vao = VAO()
        self.vao.buffer(self.vbo_vertices, "3f4", "in_position")
        self.vao.buffer(self.vbo_normals, "3f4", "in_normal")
        self.vao.buffer(self.vbo_colors, "4f4", "in_color")
        self.vao.index_buffer(self.vbo_indices)

        if self.instance_transforms is not None:
            self.vbo_instance_transforms = ctx.buffer(
                np.transpose(self.current_instance_transforms.astype("f4"), (0, 2, 1)).tobytes()
            )
            self.vao.buffer(self.vbo_instance_transforms, "16f4/i", "instance_transform")

        # Compute shape of 2D texture.
        shape = (min(self.faces.shape[0], 8192), (self.faces.shape[0] + 8191) // 8192)
        self.face_colors_texture = ctx.texture(shape, 4, dtype="f4")
        if self.face_colors is not None:
            # Write texture left justifying the buffer to fill the last row of the texture.
            self.face_colors_texture.write(
                self.current_face_colors.astype("f4").tobytes().ljust(shape[0] * shape[1] * 16)
            )

        if self.has_texture:
            img = self.texture_image
            if self.use_pickle_texture:
                self.texture = ctx.texture(img.shape[:2], img.shape[2], img.tobytes())
            else:
                self.texture = ctx.texture(img.size, 3, img.tobytes())
            self.texture_prog = get_smooth_lit_texturized_program(vs)
            self.vbo_uvs = ctx.buffer(self.uv_coords.astype("f4").tobytes())
            self.vao.buffer(self.vbo_uvs, "2f4", "in_uv")

    @hooked
    def release(self):
        if self.is_renderable:
            self.vao.release()
            if self.has_texture:
                self.texture.release()

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

    def render(self, camera, **kwargs):
        self._upload_buffers()
        prog = self._use_program(camera, **kwargs)
        self.vao.render(prog, moderngl.TRIANGLES, instances=self.n_instances)

    def render_positions(self, prog):
        if self.is_renderable:
            self._upload_buffers()

            prog["clip_control"].value = tuple(self.clip_control)
            prog["clip_value"].value = tuple(self.clip_value)

            self.vao.render(prog, moderngl.TRIANGLES, instances=self.n_instances)

    def _show_normals(self):
        """Create and add normals at runtime"""
        vn = self.vertex_normals

        bounds = self.bounds
        diag = np.linalg.norm(bounds[:, 0] - bounds[:, 1])

        length = 0.005 * max(diag, 1) / self.scale
        vn = vn / np.linalg.norm(vn, axis=-1, keepdims=True) * length

        # Must import here because if we do it at the top we create a circular dependency.
        from aitviewer.renderables.arrows import Arrows

        positions = self.vertices
        self.normals_r = Arrows(
            positions,
            positions + vn,
            r_base=length / 10,
            r_head=2 * length / 10,
            p=0.25,
            name="Normals",
        )
        self.normals_r.current_frame_id = self.current_frame_id
        self.add(self.normals_r)

    def gui(self, imgui):
        super(Meshes, self).gui(imgui)

        _, self.show_texture = imgui.checkbox(
            "Render Texture##render_texture{}".format(self.unique_name),
            self.show_texture,
        )
        _, self.norm_coloring = imgui.checkbox(
            "Norm Coloring##norm_coloring{}".format(self.unique_name),
            self.norm_coloring,
        )
        _, self.flat_shading = imgui.checkbox(
            "Flat shading [F]##flat_shading{}".format(self.unique_name),
            self.flat_shading,
        )
        _, self.draw_edges = imgui.checkbox("Draw edges [E]##draw_edges{}".format(self.unique_name), self.draw_edges)
        _, self.draw_outline = imgui.checkbox(
            "Draw outline##draw_outline{}".format(self.unique_name), self.draw_outline
        )

        if self.normals_r is None:
            if imgui.button("Show Normals ##show_normals{}".format(self.unique_name)):
                self._show_normals()

    def gui_context_menu(self, imgui, x: int, y: int):
        _, self.flat_shading = imgui.menu_item("Flat shading", "F", selected=self.flat_shading, enabled=True)
        _, self.draw_edges = imgui.menu_item("Draw edges", "E", selected=self.draw_edges, enabled=True)
        _, self.draw_outline = imgui.menu_item("Draw outline", selected=self.draw_outline)

        imgui.spacing()
        imgui.separator()
        imgui.spacing()
        super().gui_context_menu(imgui, x, y)

    def gui_io(self, imgui):
        if imgui.button("Export OBJ##export_{}".format(self.unique_name)):
            mesh = trimesh.Trimesh(vertices=self.current_vertices, faces=self.faces, process=False)
            mesh.export("../export/" + self.name + ".obj")

    def key_event(self, key, wnd_keys):
        if key == wnd_keys.F:
            self.flat_shading = not self.flat_shading
        elif key == wnd_keys.E:
            self.draw_edges = not self.draw_edges
