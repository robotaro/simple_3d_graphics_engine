import numpy as np

from ecs import constants
from ecs.components.component import Component


class Camera(Component):

    _type = "camera"

    def __init__(self,
                 z_near=constants.CAMERA_Z_NEAR,
                 z_far=constants.CAMERA_Z_FAR,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._z_near = z_near
        self._z_far = z_far

    @property
    def z_near(self):
        """float : The distance to the near clipping plane.
        """
        return self._z_near

    @z_near.setter
    def z_near(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('z-near must be >= 0.0')
        self._z_near = value

    @property
    def z_far(self):
        """float : The distance to the far clipping plane.
        """
        return self._z_far

    @z_far.setter
    def z_far(self, value):
        value = float(value)
        if value <= 0 or value <= self._z_near:
            raise ValueError('zfar must be >0 and >znear')
        self._z_far = value

    def get_view_matrix(self) -> np.ndarray:
        return np.eye(4, dtype=np.float32)

    def get_projection_matrix(self, width: int, height: int) -> np.ndarray:
        return np.eye(4, dtype=np.float32)


class PerspectiveCamera(Camera):

    def __init__(self,
                 y_fov_deg: float,
                 aspect_ratio: float,
                 z_near=constants.CAMERA_Z_NEAR,
                 z_far=constants.CAMERA_Z_FAR,
                 **kwargs):
        super(PerspectiveCamera, self).__init__(
            z_near=z_near,
            z_far=z_far,
            **kwargs
        )

        self.y_fov_deg = y_fov_deg
        self.aspect_ratio = aspect_ratio

    def get_view_matrix(self):

        return self.transform

    def get_projection_matrix(self, width: int, height: int):
        # TODO: Remove this and use the mat4 version
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """

        aspect_ratio = float(width) / float(height)

        a = aspect_ratio
        y_fov_rad = self.y_fov_deg * np.pi / 180.0
        t = np.tan(y_fov_rad / 2.0)
        n = self.z_near
        f = self.z_far

        projection_matrix = np.zeros((4, 4), dtype=np.float32)
        projection_matrix[0][0] = 1.0 / (a * t)
        projection_matrix[1][1] = 1.0 / t
        projection_matrix[3][2] = -1.0

        if f is None:
            projection_matrix[2][2] = -1.0
            projection_matrix[2][3] = -2.0 * n
        else:
            projection_matrix[2][2] = (f + n) / (n - f)
            projection_matrix[2][3] = (2 * f * n) / (n - f)

        return projection_matrix
