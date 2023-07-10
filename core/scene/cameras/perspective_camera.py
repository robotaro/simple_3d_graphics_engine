


class PerspectiveCamera(Camera):
    """
    Your classic pinhole camera.
    """

    def __init__(
        self,
        position,
        target,
        cols,
        rows,
        fov=45,
        near=None,
        far=None,
        viewer=None,
        **kwargs,
    ):
        positions = position if len(position.shape) == 2 else position[np.newaxis]
        targets = target if len(target.shape) == 2 else target[np.newaxis]
        assert (
            positions.shape[0] == 1 or targets.shape[0] == 1 or positions.shape[0] == targets.shape[0]
        ), f"position and target array shape mismatch: {positions.shape} and {targets.shape}"

        self._world_up = np.array([0.0, 1.0, 0.0])
        self._targets = targets
        super(PerspectiveCamera, self).__init__(position=position, n_frames=targets.shape[0], viewer=viewer, **kwargs)

        self.cols = cols
        self.rows = rows

        self.near = near if near is not None else C.znear
        self.far = far if far is not None else C.zfar
        self.fov = fov

    @property
    def forward(self):
        forward = self.current_target - self.position
        forward = forward / np.linalg.norm(forward)
        return forward / np.linalg.norm(forward)

    @property
    def up(self):
        up = np.cross(self.forward, self.right)
        return up

    @property
    def right(self):
        right = np.cross(self._world_up, self.forward)
        return right / np.linalg.norm(right)

    @property
    def current_target(self):
        return self._targets[0] if self._targets.shape[0] == 1 else self._targets[self.current_frame_id]

    @property
    def rotation(self):
        return np.array([-self.right, self.up, -self.forward]).T

    def update_matrices(self, width, height):
        # Compute projection matrix.
        P = perspective_projection(np.deg2rad(self.fov), width / height, self.near, self.far)

        # Compute view matrix.
        V = look_at(self.position, self.current_target, self._world_up)

        # Update camera matrices.
        self.projection_matrix = P.astype("f4")
        self.view_matrix = V.astype("f4")
        self.view_projection_matrix = np.matmul(P, V).astype("f4")

    def to_opencv_camera(self, **kwargs) -> OpenCVCamera:
        """
        Returns a OpenCVCamera object with extrinsics and intrinsics computed from this camera.
        """
        # Save current frame id.
        current_frame_id = self.current_frame_id

        cols, rows = self.cols, self.rows
        # Compute extrinsics for each frame.
        Rts = np.zeros((self.n_frames, 3, 4))
        for i in range(self.n_frames):
            self.current_frame_id = i
            self.update_matrices(cols, rows)
            Rts[i] = self.get_view_matrix()[:3]

        # Restore current frame id.
        self.current_frame_id = current_frame_id

        # Invert Y and Z to meet OpenCV conventions.
        Rts[:, 1:3, :] *= -1.0

        # Compute intrinsics.
        f = 1.0 / np.tan(np.radians(self.fov / 2))
        c0 = np.array([cols / 2.0, rows / 2.0])
        K = np.array(
            [
                [f * 0.5 * rows, 0.0, c0[0]],
                [0.0, f * 0.5 * rows, c0[1]],
                [0.0, 0.0, 1.0],
            ]
        )

        return OpenCVCamera(
            K,
            Rts,
            cols,
            rows,
            near=self.near,
            far=self.far,
            viewer=self.viewer,
            **kwargs,
        )

    def gui_affine(self, imgui):
        """Render GUI for affine transformations"""
        # Position controls
        u, pos = imgui.drag_float3(
            "Position##pos{}".format(self.unique_name),
            *self.position,
            0.1,
            format="%.2f",
        )
        if u:
            self.position = pos

    @hooked
    def gui(self, imgui):
        u, show = imgui.checkbox("Show frustum", self.frustum is not None)
        if u:
            if show:
                self.show_frustum(self.cols, self.rows, self.far)
            else:
                self.hide_frustum()

    @hooked
    def gui_context_menu(self, imgui, x: int, y: int):
        u, show = imgui.checkbox("Show frustum", self.frustum is not None)
        if u:
            if show:
                self.show_frustum(self.cols, self.rows, self.far)
            else:
                self.hide_frustum()

        imgui.spacing()
        imgui.separator()
        imgui.spacing()
        super(Camera, self).gui_context_menu(imgui, x, y)