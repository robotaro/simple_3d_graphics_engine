"""
Copyright (C) 2022  ETH Zurich, Manuel Kaufmann, Velko Vechev, Dario Mylonopoulos

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from functools import lru_cache
import moderngl
import numpy as np

from core.settings import SETTINGS
from core.math import so3
from core.scene.material import Material


class Node(object):

    def __init__(
        self,
        name=None,
        icon=None,
        position=None,
        rotation=None,
        scale=1.0,
        color=(0.5, 0.5, 0.5, 1.0),
        material=None,
        is_selectable=True,
        gui_affine=True,
        gui_material=True
    ):
        """
        :param name: Name of the node
        :param icon: Custom Node Icon using custom Icon font
        :param position: Starting position in the format (X,Y,Z) or np array of positions with shape (F, 3)
        :param rotation: Starting rotation in rotation matrix representation (3,3) or np array of rotations with shape (F, 3, 3)
        :param scale: Starting scale (scalar) or np array of scale values with shape (F)
        :param color: (R,G,B,A) 0-1 formatted color value.
        :param material: Object material properties. The color specified in the material will override node color
        :param is_selectable: If True the node is selectable when clicked on, otherwise the parent node will be selected.
        :param gui_affine: If True the node will have transform controls (position, rotation, scale) in the GUI.
        :param gui_material: If True the node will have material controls in the GUI.
        :param enabled_frames: Numpy array of boolean values, the object will be enabled only in frames where the value is True,
         the number of ones in the mask must match the number of frames of the object.
        :param n_frames: How many frames this renderable has.
        """
        # Transform & Animation
        position = np.zeros(3, dtype=np.float32) if position is None else np.array(position, dtype=np.float32)
        rotation = np.eye(3, dtype=np.float32) if rotation is None else np.array(rotation, dtype=np.float32)

        self._positions = position if len(position.shape) != 1 else position[np.newaxis]
        self._rotations = rotation if len(rotation.shape) != 2 else rotation[np.newaxis]
        self._scales = (scale if isinstance(scale, np.ndarray) else np.array([scale])).astype(np.float32)

        # Frames
        self.model_matrix = self.get_local_transform()

        # Material
        self.material = Material(color=color) if material is None else material

        # Renderable Attributes
        self.is_renderable = False
        self.backface_culling = True
        self.backface_fragmap = False
        self.draw_outline = False

        # Flags to enable rendering passes
        self.cast_shadow = False
        self.depth_prepass = False
        self.fragmap = False
        self.outline = False

        # Programs for render passes. Subclasses are responsible for setting these.
        self.depth_only_program = None  # Required for depth_prepass and cast_shadow passes
        self.fragmap_program = None  # Required for fragmap pass
        self.outline_program = None  # Required for outline pass

        # GUI
        self.name = name if name is not None else type(self).__name__
        self.uid = SETTINGS.next_gui_id()
        self.unique_name = self.name + "{}".format(self.uid)
        self.icon = icon if icon is not None else "\u0082"
        self._enabled = True
        self._expanded = False
        self.gui_controls = {
            "affine": {
                "fn": self.gui_affine,
                "icon": "\u009b",
                "is_visible": gui_affine,
            },
            "material": {
                "fn": self.gui_material,
                "icon": "\u0088",
                "is_visible": gui_material,
            },
            "io": {
                "fn": self.gui_io,
                "icon": "\u009a",
                "is_visible": (lambda: self.gui_io.__func__ is not Node.gui_io)(),
            },
        }
        self.gui_modes = {"view": {"title": " View", "fn": self.gui_mode_view, "icon": "\u0099"}}
        self._selected_mode = "view"
        self._show_in_hierarchy = True
        self.is_selectable = is_selectable

        self.nodes = []
        self.parent = None

    # Selected Mode
    @property
    def selected_mode(self):
        return self._selected_mode

    @selected_mode.setter
    def selected_mode(self, selected_mode):
        self._selected_mode = selected_mode

    # Transform
    @property
    def position(self):
        idx = self.current_frame_id if self._positions.shape[0] > 1 else 0
        return self._positions[idx]

    @position.setter
    def position(self, position):
        idx = self.current_frame_id if self._positions.shape[0] > 1 else 0
        self._positions[idx] = np.array(position, dtype=np.float32).copy()
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, positions):
        self._positions = positions
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @property
    def rotation(self):
        idx = self.current_frame_id if self._rotations.shape[0] > 1 else 0
        return self._rotations[idx]

    @rotation.setter
    def rotation(self, rotation):
        idx = self.current_frame_id if self._rotations.shape[0] > 1 else 0
        self._rotations[idx] = rotation
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @property
    def rotations(self):
        return self._rotations

    @rotations.setter
    def rotations(self, rotations):
        self._rotations = rotations
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @property
    def scale(self):
        idx = self.current_frame_id if self._scales.shape[0] > 1 else 0
        return self._scales[idx]

    @scale.setter
    def scale(self, scale):
        idx = self.current_frame_id if self._scales.shape[0] > 1 else 0
        self._scales[idx] = scale
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @property
    def scales(self):
        return self._scales

    @scales.setter
    def scales(self, scales):
        self._scales = scales
        self.update_transform(None if self.parent is None else self.parent.model_matrix)

    @staticmethod
    @lru_cache()
    def _compute_transform(pos, rot, scale):
        rotation = np.eye(4)
        rotation[:3, :3] = np.array(rot)

        trans = np.eye(4)
        trans[:3, 3] = np.array(pos)

        scale = np.diag([scale, scale, scale, 1])

        return (trans @ rotation @ scale).astype("f4")

    def get_local_transform(self):
        """Construct local transform as a 4x4 matrix from this node's position, orientation and scale."""
        return self._compute_transform(tuple(self.position), tuple(map(tuple, self.rotation)), self.scale)

    def update_transform(self, parent_transform=None):
        """Update the model matrix of this node and all of its descendants."""
        if parent_transform is None:
            self.model_matrix = self.get_local_transform()
        else:
            self.model_matrix = parent_transform.astype("f4") @ self.get_local_transform()

        for n in self.nodes:
            n.update_transform(self.model_matrix)

    @property
    def color(self):
        return self.material.color

    @color.setter
    def color(self, color):
        self.material.color = color

    @property
    def bounds(self):
        """The bounds in the format ((x_min, x_max), (y_min, y_max), (z_min, z_max))"""
        return np.array([[0, 0], [0, 0], [0, 0]])

    @property
    def current_bounds(self):
        return np.array([[0, 0], [0, 0], [0, 0]])

    @property
    def current_center(self):
        return self.current_bounds.mean(-1)

    @property
    def center(self):
        return self.bounds.mean(-1)

    def get_local_bounds(self, points):
        if len(points.shape) == 2 and points.shape[-1] == 3:
            points = points[np.newaxis]
        assert len(points.shape) == 3

        # Compute min and max coordinates of the bounding box ignoring NaNs.
        val = np.array(
            [
                [np.nanmin(points[:, :, 0]), np.nanmax(points[:, :, 0])],
                [np.nanmin(points[:, :, 1]), np.nanmax(points[:, :, 1])],
                [np.nanmin(points[:, :, 2]), np.nanmax(points[:, :, 2])],
            ]
        )

        # If any of the elements is NaN return an empty bounding box.
        if np.isnan(val).any():
            return np.array([[0, 0], [0, 0], [0, 0]])
        else:
            return val

    def get_bounds(self, points):
        val = self.get_local_bounds(points)

        # Transform bounding box with the model matrix.
        val = (self.model_matrix @ np.vstack((val, np.array([1.0, 1.0]))))[:3]

        # If any of the elements is NaN return an empty bounding box.
        if np.isnan(val).any():
            return np.array([[0, 0], [0, 0], [0, 0]])
        else:
            return val

    def add(self, *nodes, **kwargs):
        self._add_nodes(*nodes, **kwargs)

    def _add_node(self, n: "Node", show_in_hierarchy=True, expanded=False, enabled=True):
        """
        Add a single node
        :param show_in_hierarchy: Whether to show the node in the scene hierarchy.
        :param expanded: Whether the node is initially expanded in the GUI.
        """
        if n is None:
            return
        n._show_in_hierarchy = show_in_hierarchy
        n._expanded = expanded
        n._enabled = enabled if n._enabled_frames is None else n._enabled_frames[n.current_frame_id]
        self.nodes.append(n)
        n.parent = self
        n.update_transform(self.model_matrix)

    def _add_nodes(self, *nodes, **kwargs):
        """Add multiple nodes"""
        for n in nodes:
            self._add_node(n, **kwargs)

    def remove(self, *nodes):
        for n in nodes:
            n.release()
            try:
                self.nodes.remove(n)
            except:
                pass

    @property
    def show_in_hierarchy(self):
        return self._show_in_hierarchy

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, expanded):
        self._expanded = expanded

    def is_transparent(self):
        """
        Returns true if the object is transparent and should thus be sorted when rendering.
        Subclassess that use a different color should implement this method to be rendered correctly when transparent.
        """
        return self.material.color[3] < 1.0

    def gui(self, imgui):
        """
        Render GUI for custom node properties and controls. Implementation optional.
        Elements rendered here will show up in the scene hierarchy
        :param imgui: imgui context.
        See https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html for available elements to render
        """
        pass

    def gui_modes(self, imgui):
        """Render GUI with toolbar (tools) for this particular node"""

    def gui_animation(self, imgui):
        """Render GUI for animation related settings"""

        if self._enabled_frames is None:
            if self.n_frames > 1:
                u, fid = imgui.slider_int(
                    "Frame##r_{}".format(self.unique_name),
                    self.current_frame_id,
                    min_value=0,
                    max_value=self.n_frames - 1,
                )
                if u:
                    self.current_frame_id = fid
        else:
            u, fid = imgui.slider_int(
                "Frame##r_{}".format(self.unique_name),
                self._internal_frame_id,
                min_value=0,
                max_value=self._enabled_frames.shape[0] - 1,
            )
            if u:
                self.current_frame_id = fid

    def gui_affine(self, imgui):
        """Render GUI for affine transformations"""
        # Position controls
        up, pos = imgui.drag_float3(
            "Position##pos{}".format(self.unique_name),
            *self.position,
            1e-2,
            format="%.2f",
        )
        if up:
            self.position = pos

        # Rotation controls
        euler_angles = so3.rot2euler_numpy(self.rotation[np.newaxis], degrees=True)[0]
        ur, euler_angles = imgui.drag_float3(
            "Rotation##pos{}".format(self.unique_name),
            *euler_angles,
            1e-2,
            format="%.2f",
        )
        if ur:
            self.rotation = so3.euler2rot_numpy(np.array(euler_angles)[np.newaxis], degrees=True)[0]

        # Scale controls
        us, scale = imgui.drag_float(
            "Scale##scale{}".format(self.unique_name),
            self.scale,
            1e-2,
            min_value=0.001,
            max_value=100.0,
            format="%.3f",
        )
        if us:
            self.scale = scale

    def gui_material(self, imgui):
        """Render GUI with material properties"""

        # Color Control
        uc, color = imgui.color_edit4("Color##color{}'".format(self.unique_name), *self.material.color)
        if uc:
            self.color = color

        # Diffuse
        ud, diffuse = imgui.slider_float(
            "Diffuse##diffuse{}".format(self.unique_name),
            self.material.diffuse,
            0.0,
            1.0,
            "%.2f",
        )
        if ud:
            self.material.diffuse = diffuse

        # Ambient
        ua, ambient = imgui.slider_float(
            "Ambient##ambient{}".format(self.unique_name),
            self.material.ambient,
            0.0,
            1.0,
            "%.2f",
        )
        if ua:
            self.material.ambient = ambient

    def gui_io(self, imgui):
        """Render GUI for import/export"""
        pass

    def gui_mode_view(self, imgui):
        """Render custom GUI for view mode"""
        pass

    def gui_context_menu(self, imgui, x: int, y: int):
        _, self.enabled = imgui.checkbox("Enabled", self.enabled)
        if any([n._show_in_hierarchy for n in self.nodes]):
            imgui.spacing()
            imgui.separator()
            imgui.spacing()
            for n in self.nodes:
                if not n._show_in_hierarchy:
                    continue
                if imgui.begin_menu(f"{n.name}##{n.uid}"):
                    n.gui_context_menu(imgui, x, y)
                    imgui.end_menu()

    # Renderable
    @staticmethod
    def once(func):
        def _decorator(self, *args, **kwargs):
            if self.is_renderable:
                return
            else:
                func(self, *args, **kwargs)
                self.is_renderable = True

        return _decorator

    def make_renderable(self, ctx):
        """
        Prepares this object for rendering. This function must be called before `render` is used.
        :param ctx: The moderngl context.
        """
        pass

    def render(self, camera, position=None, rotation=None, **kwargs):
        """Render the current frame in this sequence."""
        pass

    def render_positions(self, prog):
        """
        Render with a VAO with only positions bound, used for shadow mapping, fragmap and depth prepass.
        """
        pass

    def redraw(self, **kwargs):
        """Perform update and redraw operations. Push to the GPU when finished. Recursively redraw child nodes"""
        for n in self.nodes:
            n.redraw(**kwargs)

    def set_camera_matrices(self, prog, camera, **kwargs):
        """Set the model view projection matrix in the given program."""
        # Transpose because np is row-major but OpenGL expects column-major.
        prog["model_matrix"].write(self.model_matrix.T.astype("f4").tobytes())
        prog["view_projection_matrix"].write(camera.get_view_projection_matrix().T.astype("f4").tobytes())

    def receive_shadow(self, program, **kwargs):
        """
        Call this function if the renderable is to receive shadows.
        :param program: The shader program that can shade with shadows.
        :param kwargs: The render kwargs.
        """
        if kwargs.get("shadows_enabled", False):
            lights = kwargs["lights"]

            for i, light in enumerate(lights):
                if light.shadow_enabled and light.shadow_map:
                    light_matrix = light.mvp() @ self.model_matrix
                    program[f"dirLights[{i}].matrix"].write(light_matrix.T.tobytes())

                    # Bind shadowmap to slot i + 1, we reserve slot 0 for the mesh texture
                    # and use slots 1 to (#lights + 1) for shadow maps
                    light.shadow_map.use(location=i + 1)

            # Set sampler uniforms
            uniform = program[f"shadow_maps"]
            uniform.value = 1 if uniform.array_length == 1 else [*range(1, len(lights) + 1)]

    def render_shadowmap(self, light_matrix):
        if not self.cast_shadow or self.depth_only_program is None or self.color[3] == 0.0:
            return

        prog = self.depth_only_program
        prog["model_matrix"].write(self.model_matrix.T.tobytes())
        prog["view_projection_matrix"].write(light_matrix.T.tobytes())

        self.render_positions(prog)

    def render_fragmap(self, ctx, camera, uid=None):
        if not self.fragmap or self.fragmap_program is None:
            return

        # Transpose because np is row-major but OpenGL expects column-major.
        prog = self.fragmap_program
        self.set_camera_matrices(prog, camera)

        # Render with the specified object uid, if None use the node uid instead.
        prog["obj_id"] = uid or self.uid

        if self.backface_culling or self.backface_fragmap:
            ctx.enable(moderngl.CULL_FACE)
        else:
            ctx.disable(moderngl.CULL_FACE)

        # If backface_fragmap is enabled for this node only render backfaces
        if self.backface_fragmap:
            ctx.cull_face = "front"

        self.render_positions(prog)

        # Restore cull face to back
        if self.backface_fragmap:
            ctx.cull_face = "back"

    def render_depth_prepass(self, camera, **kwargs):
        if not self.depth_prepass or self.depth_only_program is None:
            return

        prog = self.depth_only_program
        self.set_camera_matrices(prog, camera)
        self.render_positions(prog)

    def render_outline(self, ctx, camera):
        if self.outline and self.outline_program is not None:
            prog = self.outline_program
            self.set_camera_matrices(prog, camera)

            if self.backface_culling:
                ctx.enable(moderngl.CULL_FACE)
            else:
                ctx.disable(moderngl.CULL_FACE)
            self.render_positions(prog)

        # Render children node recursively.
        for n in self.nodes:
            n.render_outline(ctx, camera)

    def release(self):
        """
        Release all OpenGL resources used by this node and any of its children. Subclasses that instantiate OpenGL
        objects should implement this method with '@hooked' to avoid leaking resources.
        """
        for n in self.nodes:
            n.release()

    def on_selection(self, node, instance_id, tri_id):
        """
        Called when the node is selected

        :param node:  the node which was clicked (can be None if the selection wasn't a mouse event)
        :param instance_id: the id of the instance that was clicked, 0 if the object is not instanced
                            (can be None if the selection wasn't a mouse event)
        :param tri_id: the id of the triangle that was clicked from the 'node' mesh
                       (can be None if the selection wasn't a mouse event)
        """
        pass

    def key_event(self, key, wnd_keys):
        """
        Handle shortcut key presses (if you are the selected object)
        """
        pass

    def update_frames(self, *args, **kwargs):
        pass

    def add_frames(self, *args, **kwargs):
        pass

    def remove_frames(self, *args, **kwargs):
        pass
