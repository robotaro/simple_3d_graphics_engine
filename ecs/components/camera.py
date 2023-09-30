import numpy as np
import moderngl

from ecs import constants
from ecs.components.component import Component
from ecs.utilities import utils_camera


class Camera(Component):

    _type = "camera"

    __slots__ = [
        "y_fov_deg",
        "z_near",
        "z_far",
        "orthographic_scale",
        "viewport_norm",
        "viewport_pixels",
        "perspective"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.z_near = kwargs.get("z_near", constants.CAMERA_Z_NEAR)
        self.z_far = kwargs.get("z_far", constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # Orthographic variables
        self.orthographic_scale = 1.0

        self.viewport_norm = kwargs.get("viewport_norm", constants.CAMERA_VIEWPORT_NORM)
        self.viewport_pixels = None

        # Flags
        self.perspective = kwargs.get("perspective", True)

    def upload_uniforms(self, program: moderngl.Program, window_width: int, window_height: int):
        proj_matrix_bytes = self.get_projection_matrix(window_width=window_width,
                                                       window_height=window_height).T.tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

    def update_viewport(self, window_size: tuple):
        self.viewport_pixels = (int(self.viewport_norm[0] * window_size[0]),
                                int(self.viewport_norm[1] * window_size[1]),
                                int(self.viewport_norm[2] * window_size[0]),
                                int(self.viewport_norm[3] * window_size[1]))

    def get_projection_matrix(self, window_width: int, window_height: int):

        nom = window_width * (self.viewport_norm[2] - self.viewport_norm[0])
        den = window_height * (self.viewport_norm[3] - self.viewport_norm[1])
        aspect_ratio = nom / den

        if self.perspective:
            return utils_camera.perspective_projection(
                fov_rad=self.y_fov_deg * np.pi / 180.0,  # TODO: OPtimise deg2rad conversion
                aspect_ratio=aspect_ratio,
                z_near=self.z_near,
                z_far=self.z_far)
        else:
            return utils_camera.orthographic_projection(
                scale_x=self.orthographic_scale * aspect_ratio,
                scale_y=self.orthographic_scale,
                z_near=self.z_near,
                z_far=self.z_far)

