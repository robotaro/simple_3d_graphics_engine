import numpy as np
import moderngl

from ecs import constants
from ecs.components.component import Component


class Camera(Component):

    _type = "camera"

    __slots__ = [
        "z_near",
        "z_far",
        "x_mag",
        "y_mag",
        "viewport_norm",
        "viewport"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.z_near = kwargs.get("z_near", constants.CAMERA_Z_NEAR)
        self.z_far = kwargs.get("z_far", constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # TODO: Figure out how to use these values
        # Orthographic variables
        self.x_mag = 1.0
        self.y_mag = 1.0

        self.viewport_norm = kwargs.get("viewport_norm", constants.CAMERA_VIEWPORT_NORM)
        self.viewport = None

    def upload_uniforms(self, program: moderngl.Program, window_width: int, window_height: int):

        proj_matrix_bytes = self.get_projection_matrix(window_width=window_width,
                                                       window_height=window_height).T.tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

    def get_projection_matrix(self, window_width: int, window_height: int):

        num = window_width * (self.viewport_norm[2] - self.viewport_norm[0])
        den = window_height * (self.viewport_norm[3] - self.viewport_norm[1])
        aspect_ratio = num / den

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

    def get_orthographic_matrix(self, window_width: int, window_height: int):

        # TODO: Test this

        xmag = self.x_mag
        ymag = self.y_mag

        # If screen width/height defined, rescale xmag
        if window_width is not None and window_height is not None:
            xmag = window_width / window_height * ymag

        n = self.z_near
        f = self.z_far
        projection_matrix = np.zeros((4, 4))
        projection_matrix[0][0] = 1.0 / xmag
        projection_matrix[1][1] = 1.0 / ymag
        projection_matrix[2][2] = 2.0 / (n - f)
        projection_matrix[2][3] = (f + n) / (n - f)
        projection_matrix[3][3] = 1.0

        return projection_matrix
