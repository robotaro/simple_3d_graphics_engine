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
        "y_mag"
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

        if "viewport" not in kwargs:
            raise Exception(f"[ERROR] Camera needs a viewport argument")

        self.viewport = kwargs["viewport"]

    def upload_uniforms(self, program: moderngl.Program):

        proj_matrix_bytes = self.get_projection_matrix(
            width=self.viewport[constants.VIEWPORT_INDEX_WIDTH],
            height=self.viewport[constants.VIEWPORT_INDEX_HEIGHT]).T.astype('f4').tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

    def get_projection_matrix(self, width: int, height: int):

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

    def get_orthographic_matrix(self, width: int, height: int):

        xmag = self.x_mag
        ymag = self.y_mag

        # If screen width/height defined, rescale xmag
        if width is not None and height is not None:
            xmag = width / height * ymag

        n = self.z_near
        f = self.z_far
        projection_matrix = np.zeros((4, 4))
        projection_matrix[0][0] = 1.0 / xmag
        projection_matrix[1][1] = 1.0 / ymag
        projection_matrix[2][2] = 2.0 / (n - f)
        projection_matrix[2][3] = (f + n) / (n - f)
        projection_matrix[3][3] = 1.0

        return projection_matrix
