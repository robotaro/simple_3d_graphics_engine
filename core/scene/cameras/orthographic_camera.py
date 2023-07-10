


class OrthographicCamera(Camera):
    """
    A sequence of weak perspective cameras.
    The camera is positioned at (0,0,1) axis aligned and looks towards the negative z direction following the OpenGL
    conventions.
    """

    def __init__(
        self,
        scale,
        translation,
        cols,
        rows,
        near=None,
        far=None,
        viewer=None,
        **kwargs,
    ):
        """Initializer.
        :param scale: A np array of scale parameters [sx, sy] of shape (2) or a sequence of parameters of shape (N, 2)
        :param translation: A np array of translation parameters [tx, ty] of shape (2) or a sequence of parameters of
          shape (N, 2).
        :param cols: Number of columns in an image captured by this camera, used for computing the aspect ratio of
          the camera.
        :param rows: Number of rows in an image captured by this camera, used for computing the aspect ratio of
          the camera.
        :param near: Distance of the near plane from the camera.
        :param far: Distance of the far plane from the camera.
        :param viewer: the current viewer, if not None the gui for this object will show a button for viewing from
          this camera in the viewer.
        """
        if len(scale.shape) == 1:
            scale = scale[np.newaxis]

        if len(translation.shape) == 1:
            translation = translation[np.newaxis]

        assert scale.shape[0] == translation.shape[0], "Number of frames in scale and translation must match"

        kwargs["gui_affine"] = False
        super(OrthographicCamera, self).__init__(n_frames=scale.shape[0], viewer=viewer, **kwargs)

        self.scale_factor = scale
        self.translation = translation

        self.cols = cols
        self.rows = rows
        self.near = near if near is not None else C.znear
        self.far = far if far is not None else C.zfar
        self.viewer = viewer

        self.position = np.array([0, 0, 1], dtype=np.float32)
        self._right = np.array([1, 0, 0], dtype=np.float32)
        self._up = np.array([0, 1, 0], dtype=np.float32)
        self._forward = -np.array([0, 0, 1], dtype=np.float32)

    @property
    def forward(self):
        return self._forward

    @property
    def up(self):
        return self._up

    @property
    def right(self):
        return self._right

    def update_matrices(self, width, height):
        sx, sy = self.scale_factor[self.current_frame_id]
        tx, ty = self.translation[self.current_frame_id]

        window_ar = width / height
        camera_ar = self.cols / self.rows
        ar = camera_ar / window_ar

        P = np.array(
            [
                [sx * ar, 0, 0, tx * sx * ar],
                [0, sy, 0, -ty * sy],
                [0, 0, -1, 0],
                [0, 0, 0, 1],
            ]
        )

        znear, zfar = self.near, self.far
        P[2][2] = 2.0 / (znear - zfar)
        P[2][3] = (zfar + znear) / (znear - zfar)

        V = look_at(self.position, self.forward, np.array([0, 1, 0]))

        # Update camera matrices
        self.projection_matrix = P.astype("f4")
        self.view_matrix = V.astype("f4")
        self.view_projection_matrix = np.matmul(P, V).astype("f4")

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