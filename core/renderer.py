from core.window import Window

class Viewport:
    def __init__(self, extents: Tuple[int, int, int, int], camera: CameraInterface):
        self.extents = extents
        self._camera = camera
        self._using_temp_camera = not isinstance(camera, ViewerCamera)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera: CameraInterface):
        self._camera = camera
        self._using_temp_camera = not isinstance(camera, ViewerCamera)

    def contains(self, x: int, y: int):
        e = self.extents
        return x >= e[0] and x < e[0] + e[2] and y >= e[1] and y < e[1] + e[3]

    def set_temp_camera(self, camera: CameraInterface):
        self.camera = camera
        self._using_temp_camera = True

    def reset_camera(self):
        if self._using_temp_camera:
            self._using_temp_camera = False

            fwd = self.camera.forward
            pos = self.camera.position

            self.camera = ViewerCamera(45)
            self.camera.position = np.copy(pos)
            self.camera.target = pos + fwd * 3
            self.camera.update_matrices(*self.extents[2:])

class Renderer:

    def __init__(self, window: Window):
        self.window = window

    def render_viewport(self, viewport: tuple):