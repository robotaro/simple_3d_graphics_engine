import numpy as np

from ecs import constants
from ecs.components.component import Component


class PerspectiveCamera(Component):

    _type = "perspective_camera"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.z_near = constants.CAMERA_Z_NEAR
        self.z_far = constants.CAMERA_Z_FAR
        self.y_fov_deg = constants.CAMERA_FOV_DEG

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
