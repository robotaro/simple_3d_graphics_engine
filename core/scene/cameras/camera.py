import numpy as np


from core.scene.node import Node
from core.scene.cameras.camera_interface import CameraInterface


class Camera(Node, CameraInterface):
    """
    A base camera object that provides rendering of a camera mesh and visualization of the camera frustum and coordinate
    system. Subclasses of this class must implement the CameraInterface abstract methods.
    """

    def __init__(
        self,
        inactive_color=(0.5, 0.5, 0.5, 1),
        active_color=(0.6, 0.1, 0.1, 1),
        viewer=None,
        **kwargs,
    ):
        """Initializer
        :param inactive_color: Color that will be used for rendering this object when inactive
        :param active_color:   Color that will be used for rendering this object when active
        :param viewer: The current viewer, if not None the gui for this object will show a button for viewing from this
         camera in the viewer
        """
        super(Camera, self).__init__(icon="\u0084", gui_material=False, **kwargs)

        # Camera object geometry
        vertices = np.array(
            [
                # Body
                [0, 0, 0],
                [-1, -1, 1],
                [-1, 1, 1],
                [1, -1, 1],
                [1, 1, 1],
                # Triangle front
                [0.5, 1.1, 1],
                [-0.5, 1.1, 1],
                [0, 2, 1],
                # Triangle back
                [0.5, 1.1, 1],
                [-0.5, 1.1, 1],
                [0, 2, 1],
            ],
            dtype=np.float32,
        )

        # Scale dimensions
        vertices[:, 0] *= 0.05
        vertices[:, 1] *= 0.03
        vertices[:, 2] *= 0.15

        # Slide such that the origin is in front of the object
        vertices[:, 2] -= vertices[1, 2] * 1.1

        # Reverse z since we use the opengl convention that camera forward is -z
        vertices[:, 2] *= -1

        # Reverse x too to maintain a consistent triangle winding
        vertices[:, 0] *= -1

        faces = np.array(
            [
                [0, 1, 2],
                [0, 2, 4],
                [0, 4, 3],
                [0, 3, 1],
                [1, 3, 2],
                [4, 2, 3],
                [5, 6, 7],
                [8, 10, 9],
            ]
        )

        self._active = False
        self.active_color = active_color
        self.inactive_color = inactive_color

        self.mesh = Meshes(
            vertices,
            faces,
            cast_shadow=False,
            flat_shading=True,
            rotation=kwargs.get("rotation"),
            is_selectable=False,
        )
        self.mesh.color = self.inactive_color
        self.add(self.mesh, show_in_hierarchy=False)

        self.frustum = None
        self.origin = None
        self.path = None

        self.viewer = viewer

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active

        if active:
            self.mesh.color = self.active_color
        else:
            self.mesh.color = self.inactive_color

    @Node.enabled.setter
    def enabled(self, enabled):
        # Call setter of the parent (Node) class.
        super(Camera, self.__class__).enabled.fset(self, enabled)

        # Also set the enabled property of the path if it exists.
        # We must do this here because the path is not a child of the camera node,
        # since it's position/rotation should not be updated together with the camera.
        if self.path:
            self.path[0].enabled = enabled
            if self.path[1] is not None:
                self.path[1].enabled = enabled

    @property
    def bounds(self):
        return self.mesh.bounds

    @property
    def current_bounds(self):
        return self.mesh.current_bounds

    def hide_frustum(self):
        if self.frustum:
            self.remove(self.frustum)
            self.frustum = None

        if self.origin:
            self.remove(self.origin)
            self.origin = None

    def show_frustum(self, width, height, distance):
        # Remove previous frustum if it exists
        self.hide_frustum()

        # Compute lines for each frame
        """all_lines = np.zeros((self.n_frames, 24, 3), dtype=np.float32)
        frame_id = self.current_frame_id
        for i in range(self.n_frames):
            # Set the current frame id to use the camera matrices from the respective frame
            self.current_frame_id = i

            # Compute frustum coordinates
            self.update_matrices(width, height)
            P = self.get_projection_matrix()
            ndc_from_view = P
            view_from_ndc = np.linalg.inv(ndc_from_view)

            def transform(x):
                v = view_from_ndc @ np.append(x, 1.0)
                return v[:3] / v[3]

            # Comput z coordinate of a point at the given distance
            view_p = np.array([0.0, 0.0, -distance])
            ndc_p = ndc_from_view @ np.concatenate([view_p, np.array([1])])

            # Compute z after perspective division
            z = ndc_p[2] / ndc_p[3]

            lines = np.array(
                [
                    [-1, -1, -1],
                    [-1, 1, -1],
                    [-1, -1, z],
                    [-1, 1, z],
                    [1, -1, -1],
                    [1, 1, -1],
                    [1, -1, z],
                    [1, 1, z],
                    [-1, -1, -1],
                    [-1, -1, z],
                    [-1, 1, -1],
                    [-1, 1, z],
                    [1, -1, -1],
                    [1, -1, z],
                    [1, 1, -1],
                    [1, 1, z],
                    [-1, -1, -1],
                    [1, -1, -1],
                    [-1, -1, z],
                    [1, -1, z],
                    [-1, 1, -1],
                    [1, 1, -1],
                    [-1, 1, z],
                    [1, 1, z],
                ],
                dtype=np.float32,
            )

            lines = np.apply_along_axis(transform, 1, lines)
            all_lines[i] = lines

        self.frustum = Lines(
            all_lines,
            r_base=0.005,
            mode="lines",
            color=(0.1, 0.1, 0.1, 1),
            cast_shadow=False,
        )
        self.add(self.frustum, show_in_hierarchy=False)

        ori = np.eye(3, dtype=np.float)
        ori[:, 2] *= -1
        self.origin = RigidBodies(np.array([0.0, 0.0, 0.0])[np.newaxis], ori[np.newaxis])
        self.add(self.origin, show_in_hierarchy=False)

        self.current_frame_id = frame_id"""

    def hide_path(self):
        if self.path is not None:
            self.parent.remove(self.path[0])
            # The Lines part of the path may be None if the path is a single point.
            if self.path[1] is not None:
                self.parent.remove(self.path[1])
            self.path = None

    def show_path(self):
        # Remove previous path if it exists
        self.hide_path()

        # Compute position and orientation for each frame
        """all_points = np.zeros((self.n_frames, 3), dtype=np.float32)
        all_oris = np.zeros((self.n_frames, 3, 3), dtype=np.float32)
        frame_id = self.current_frame_id
        for i in range(self.n_frames):
            # Set the current frame id to use the position and rotation for this frame
            self.current_frame_id = i

            all_points[i] = self.position
            # Flip the Z axis since we want to display the orientation with Z forward
            all_oris[i] = self.rotation @ np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]])

        path_spheres = RigidBodies(all_points, all_oris, radius=0.01, length=0.1, color=(0.92, 0.68, 0.2, 1.0))
        # Create lines only if there is more than one frame in the sequence.
        if self.n_frames > 1:
            path_lines = Lines(
                all_points,
                color=(0, 0, 0, 1),
                r_base=0.003,
                mode="line_strip",
                cast_shadow=False,
            )
        else:
            path_lines = None

        # We add the the path to the parent node of the camera because we don't want the camera position and rotation
        # to be applied to it.
        assert self.parent is not None, "Camera node must be added to the scene before showing the camera path."
        self.parent.add(path_spheres, show_in_hierarchy=False, enabled=self.enabled)
        if path_lines is not None:
            self.parent.add(path_lines, show_in_hierarchy=False, enabled=self.enabled)

        self.path = (path_spheres, path_lines)
        self.current_frame_id = frame_id"""

    def render_outline(self, *args, **kwargs):
        # Only render the mesh outline, this avoids outlining
        # the frustum and coordinate system visualization.
        self.mesh.render_outline(*args, **kwargs)

    def view_from_camera(self, viewport):
        """If the viewer is specified for this camera, change the current view to view from this camera"""
        if self.viewer:
            self.hide_path()
            self.hide_frustum()
            self.viewer.set_temp_camera(self, viewport)

    def gui(self, imgui):
        if self.viewer:
            if imgui.button("View from camera"):
                self.view_from_camera(self.viewer.viewports[0])

        u, show = imgui.checkbox("Show path", self.path is not None)
        if u:
            if show:
                self.show_path()
            else:
                self.hide_path()

    def gui_context_menu(self, imgui, x: int, y: int):
        if self.viewer:
            if imgui.menu_item("View from camera", shortcut=None, selected=False, enabled=True)[1]:
                self.view_from_camera(self.viewer.get_viewport_at_position(x, y))

        u, show = imgui.checkbox("Show path", self.path is not None)
        if u:
            if show:
                self.show_path()
            else:
                self.hide_path()