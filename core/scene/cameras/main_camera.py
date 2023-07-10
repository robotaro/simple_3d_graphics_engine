



class MainCamera(CameraInterface):
    """
    The camera used by the user - Perspective or Orthographic
    This camera also supports orbiting, panning and generating camera rays.
    """

    def __init__(self, fov=45, orthographic=None, znear=None, zfar=None):
        super(MainCamera, self).__init__()
        self.fov = fov
        self.is_ortho = orthographic is not None
        self.ortho_size = 1.0 if orthographic is None else orthographic

        # Default camera settings.
        self._position = np.array([0.0, 0.0, 2.5])
        self._target = np.array([0.0, 0.0, 0.0])
        self._up = np.array([0.0, 1.0, 0.0])

        self.ZOOM_FACTOR = 4
        self.ROT_FACTOR = 0.0025
        self.PAN_FACTOR = 0.01

        self.near = znear if znear is not None else constants.CAMERA_Z_NEAR
        self.far = zfar if zfar is not None else constants.CAMERA_Z_FAR

        # Controls options.
        self.constant_speed = 1.0
        self._control_modes = ["turntable", "trackball", "first_person"]
        self._control_mode = "turntable"
        self._trackball_start_view_inverse = None
        self._trackball_start_hit = None
        self._trackball_start_position = None
        self._trackball_start_up = None

        # GUI options.
        self.name = "Camera"
        self.icon = "\u0084"

        # Animation.
        self.animating = False
        self._animation_t = 0.0
        self._animation_time = 0.0
        self._animation_start_position = None
        self._animation_end_position = None
        self._animation_start_target = None
        self._animation_end_target = None

    @property
    def control_mode(self):
        return self._control_mode

    @control_mode.setter
    def control_mode(self, mode):
        if mode not in self._control_modes:
            raise ValueError(f"Invalid camera mode: {mode}")
        if mode == "first_person" or mode == "turntable":
            self.up = (0, 1, 0)
        self._control_mode = mode

    def copy(self):
        camera = MainCamera(self.fov, self.ortho_size, self.near, self.far)
        camera.is_ortho = self.is_ortho
        camera.position = self.position
        camera.target = self.target
        camera.up = self.up
        camera.constant_speed = self.constant_speed
        camera.control_mode = self.control_mode
        return camera

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = np.array(position, dtype=np.float32).copy()

    @property
    def forward(self):
        return utils_camera.normalize(self.target - self.position)

    @property
    def up(self):
        return self._up

    @up.setter
    def up(self, up):
        self._up = np.array(up, dtype=np.float32).copy()

    @property
    def right(self):
        return utils_camera.normalize(np.cross(self.up, self.forward))

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, t):
        self._target = np.array(t, np.float32).copy()

    def update_matrices(self, width, height):
        # Compute projection matrix.
        if self.is_ortho:
            yscale = self.ortho_size
            xscale = width / height * yscale
            proj_matrix = utils_camera.orthographic_projection(xscale, yscale, self.near, self.far)
        else:
            proj_matrix = utils_camera.perspective_projection(np.deg2rad(self.fov), width / height, self.near, self.far)

        # Compute view matrix.
        view_matrix = utils_camera.look_at(self.position, self.target, self.up)

        # Update camera matrices.
        self.projection_matrix = proj_matrix.astype("f4")
        self.view_matrix = view_matrix.astype("f4")
        self.view_projection_matrix = np.matmul(proj_matrix, view_matrix).astype("f4")

    def dolly_zoom(self, speed, move_target=False, constant_speed=False):
        """
        Zoom by moving the camera along its view direction.
        If move_target is true the camera target will also move rigidly with the camera.
        """
        # We update both the orthographic and perspective projection so that the transition is seamless when
        # transitioning between them.
        self.ortho_size -= 0.1 * np.sign(speed)
        self.ortho_size = max(0.0001, self.ortho_size)

        # Scale the speed in proportion to the norm (i.e. camera moves slower closer to the target)
        norm = max(np.linalg.norm(self.position - self.target), 2)
        fwd = self.forward

        # Adjust speed according to config
        speed *= constants.CAMERA_ZOOM_SPEED.camera_zoom_speed

        if move_target or constant_speed:
            if constant_speed:
                norm = self.constant_speed * 20
            self.position += fwd * speed * norm
            self.target += fwd * speed * norm
        else:
            # Clamp movement size to avoid surpassing the target
            movement_length = speed * norm
            max_movement_length = max(np.linalg.norm(self.target - self.position) - 0.01, 0.0)

            # Update position
            self.position += fwd * min(movement_length, max_movement_length)

    def pan(self, mouse_dx, mouse_dy):
        """Move the camera in the image plane."""
        sideways = utils_camera.normalize(np.cross(self.forward, self.up))
        up = np.cross(sideways, self.forward)

        # scale speed according to distance from target
        speed = max(np.linalg.norm(self.target - self.position) * 0.1, 0.1)

        speed_x = mouse_dx * self.PAN_FACTOR * speed
        speed_y = mouse_dy * self.PAN_FACTOR * speed

        self.position -= sideways * speed_x
        self.target -= sideways * speed_x

        self.position += up * speed_y
        self.target += up * speed_y

    def rotate_azimuth(self, angle):
        """Rotate around camera's up-axis by given angle (in radians)."""
        if np.abs(angle) < 1e-8:
            return
        cam_pose = np.linalg.inv(self.view_matrix)
        y_axis = cam_pose[:3, 1]
        rot = rotation_matrix(angle, y_axis, self.target)
        self.position = _transform_vector(rot, self.position)

    def _rotation_from_mouse_delta(self, mouse_dx: int, mouse_dy: int):
        z_axis = -self.forward
        dot = np.dot(z_axis, self.up)
        rot = np.eye(4)

        # Avoid singularity when z axis of camera is aligned with the up axis of the scene.
        if not (mouse_dy > 0 and dot > 0 and 1 - dot < 0.001) and not (mouse_dy < 0 and dot < 0 and 1 + dot < 0.001):
            # We are either hovering exactly below or above the scene's target but we want to move away or we are
            # not hitting the singularity anyway.
            x_axis = -self.right
            rot_x = rotation_matrix(self.ROT_FACTOR * -mouse_dy, x_axis, self.target)
            rot = rot_x @ rot

        y_axis = np.cross(self.forward, self.right)
        x_speed = self.ROT_FACTOR / 10 if 1 - np.abs(dot) < 0.01 else self.ROT_FACTOR
        rot = rotation_matrix(x_speed * -mouse_dx, y_axis, self.target) @ rot
        return rot

    def rotate_azimuth_elevation(self, mouse_dx: int, mouse_dy: int):
        """Rotate the camera position left-right and up-down orbiting around the target (roll is not allowed)."""
        rot = self._rotation_from_mouse_delta(mouse_dx, mouse_dy)
        self.position = _transform_vector(rot, self.position)

    def rotate_first_person(self, mouse_dx: int, mouse_dy: int):
        """Rotate the camera target left-right and up-down (roll is not allowed)."""
        rot = self._rotation_from_mouse_delta(mouse_dx, mouse_dy)
        self.target = _transform_direction(rot, self.target - self.position) + self.position

    def intersect_trackball(self, x: int, y: int, width: int, height: int):
        """
        Return intersection of a line passing through the mouse position at pixel coordinates x, y
        and the trackball as a point in world coordinates.
        """
        # Transform mouse coordinates from -1 to 1
        nx = 2 * (x + 0.5) / width - 1
        ny = 1 - 2 * (y + 0.5) / height

        # Adjust coordinates for the larger side of the viewport rectangle.
        if width > height:
            nx *= width / height
        else:
            ny *= height / width

        s = nx * nx + ny * ny
        if s <= 0.5:
            # Sphere intersection
            nz = np.sqrt(1 - s)
        else:
            # Hyperboloid intersection.
            nz = 1 / (2 * np.sqrt(s))

        # Return intersection position in world coordinates.
        return self._trackball_start_view_inverse @ np.array((nx, ny, nz))

    def rotate_trackball(self, x: int, y: int, width: int, height: int):
        """Rotate the camera with trackball controls. Must be called after rotate_start()."""
        # Compute points on trackball.
        start = self._trackball_start_hit
        current = self.intersect_trackball(x, y, width, height)
        dist = np.linalg.norm(current - start)

        # Skip if starting and current point are too close.
        if dist < 1e-6:
            return

        # Compute axis of rotation as the vector perpendicular to the plane spanned by the
        # vectors connecting the origin to the two points.
        axis = utils_camera.normalize(np.cross(current, start))

        # Compute angle as the angle between the two vectors, if they are too far away we use the distance
        # between them instead, this makes it continue to rotate when dragging the mouse further away.
        angle = max(np.arccos(np.dot(utils_camera.normalize(current), utils_camera.normalize(start))), dist)

        # Compute resulting rotation and apply it to the starting position and up vector.
        rot = rotation_matrix(angle, axis, self.target)
        self.position = _transform_vector(rot, self._trackball_start_position)
        self.up = _transform_direction(rot, self._trackball_start_up)

    def rotate_start(self, x: int, y: int, width: int, height: int):
        """Start rotating the camera. Called on mouse button press."""
        if self.control_mode == "trackball":
            self._trackball_start_view_inverse = utils_camera.look_at(self.position, self.target, self.up)[:3, :3].T
            self._trackball_start_hit = self.intersect_trackball(x, y, width, height)
            self._trackball_start_position = self.position
            self._trackball_start_up = self.up

    def rotate(self, x: int, y: int, mouse_dx: int, mouse_dy: int, width: int, height: int):
        """Rotate the camera. Called on mouse movement."""
        if self.control_mode == "turntable":
            self.rotate_azimuth_elevation(mouse_dx, mouse_dy)
        elif self.control_mode == "trackball":
            self.rotate_trackball(x, y, width, height)
        elif self.control_mode == "first_person":
            self.rotate_first_person(mouse_dx, mouse_dy)

    def get_ray(self, x, y, width, height):
        """Construct a ray going through the middle of the given pixel."""
        w, h = width, height

        # Pixel in (-1, 1) range.
        screen_x = 2 * (x + 0.5) / w - 1
        screen_y = 1 - 2 * (y + 0.5) / h

        # Scale to actual image plane size.
        scale = self.ortho_size if self.is_ortho else np.tan(np.deg2rad(self.fov) / 2)
        screen_x *= scale * w / h
        screen_y *= scale

        pixel_2d = np.array([screen_x, screen_y, 0 if self.is_ortho else -1])
        cam2world = np.linalg.inv(self.view_matrix)
        pixel_3d = _transform_vector(cam2world, pixel_2d)
        if self.is_ortho:
            ray_origin = pixel_3d
            ray_dir = self.forward
        else:
            eye_origin = np.zeros(3)
            ray_origin = _transform_vector(cam2world, eye_origin)
            ray_dir = pixel_3d - ray_origin
        ray_dir = ray_dir / np.linalg.norm(ray_dir)

        return ray_origin, ray_dir

    def move_with_animation(self, end_position, end_target, time=0.25):
        self._animation_start_position = self.position.copy()
        self._animation_end_position = np.array(end_position)
        self._animation_start_target = self.target.copy()
        self._animation_end_target = np.array(end_target)
        self._animation_total_time = time
        self._animation_t = 0.0
        self.animating = True

    def update_animation(self, dt):
        if not self.animating:
            return

        self._animation_t += dt
        if self._animation_t >= self._animation_total_time:
            self.position = self._animation_end_position
            self.target = self._animation_end_target
            self.animating = False
        else:
            t = self._animation_t / self._animation_total_time
            # Smootherstep interpolation (this polynomial has 0 first and second derivative at 0 and 1)
            t = t * t * t * (t * (t * 6 - 15) + 10)
            self.position = self._animation_start_position * (1 - t) + self._animation_end_position * t
            self.target = self._animation_start_target * (1 - t) + self._animation_end_target * t

    def gui(self, imgui):
        _, self.is_ortho = imgui.checkbox("Orthographic Camera", self.is_ortho)
        _, self.fov = imgui.slider_float("Camera FOV##fov", self.fov, 0.1, 180.0, "%.1f")
        _, self.position = imgui.drag_float3("Position", *self.position)
        _, self.target = imgui.drag_float3("Target", *self.target)
        _, self.up = imgui.drag_float3("Up", *self.up)

        imgui.spacing()
        # Note: must be kept in sync with self._control_modes.
        control_modes_labels = ["Turntable", "Trackball", "First Person"]
        u, idx = imgui.combo("Control mode", self._control_modes.index(self.control_mode), control_modes_labels)
        if u and idx >= 0 and idx <= len(self._control_modes):
            self.control_mode = self._control_modes[idx]
