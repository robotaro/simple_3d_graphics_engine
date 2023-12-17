import numpy as np

import moderngl

from src.core import constants
from src.core.component import Component
from src.utilities import utils_camera


class Camera(Component):

    _type = "camera"

    __slots__ = [
        "y_fov_deg",
        "z_near",
        "z_far",
        "orthographic_scale",
        "viewport_screen_ratio",
        "viewport_pixels",
        "is_perspective",
        "projection_matrix",
        "inverse_projection_matrix",
        "projection_matrix_dirty"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.z_near = self.dict2float(input_dict=self.parameters, key="z_near", default_value=constants.CAMERA_Z_NEAR)
        self.z_far = self.dict2float(input_dict=self.parameters, key="z_far", default_value=constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # Orthographic variables
        self.orthographic_scale = 1.0
        self.viewport_screen_ratio = self.dict2tuple_float(input_dict=self.parameters,
                                                           key="viewport_screen_ratio",
                                                           default_value=(0.0, 0.0, 1.0, 1.0))
        self.viewport_pixels = None

        # Flags
        self.is_perspective = self.dict2bool(input_dict=self.parameters, key="perspective", default_value=True)

        # Projection Matrix
        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.inverse_projection_matrix = np.eye(4, dtype=np.float32)
        self.projection_matrix_dirty = True

    def upload_uniforms(self, program: moderngl.Program):
        program["projection_matrix"].write(self.get_projection_matrix().T.tobytes())

    def update_viewport(self, window_size: tuple):

        self.viewport_pixels = (int(self.viewport_screen_ratio[0] * window_size[0]),
                                int(self.viewport_screen_ratio[1] * window_size[1]),
                                int(self.viewport_screen_ratio[2] * window_size[0]),
                                int(self.viewport_screen_ratio[3] * window_size[1]))

        self.update_projection_matrix()

    def is_inside_viewport(self, screen_gl_position: tuple) -> bool:
        if self.viewport_pixels is None:
            return False

        flag_x = self.viewport_pixels[0] <= screen_gl_position[0] < (self.viewport_pixels[2] + self.viewport_pixels[0])
        flag_y = self.viewport_pixels[1] <= screen_gl_position[1] < (self.viewport_pixels[3] + self.viewport_pixels[1])

        return flag_x & flag_y

    def update_projection_matrix(self):

        if self.viewport_pixels is None:
            return

        aspect_ratio = self.viewport_pixels[2] / self.viewport_pixels[3]
        if self.is_perspective:
            # PERSPECTIVE
            self.projection_matrix = utils_camera.perspective_projection(
                fov_rad=self.y_fov_deg * constants.DEG2RAD,
                aspect_ratio=aspect_ratio,
                z_near=self.z_near,
                z_far=self.z_far)
        else:
            # ORTHOGRAPHIC
            self.projection_matrix = utils_camera.orthographic_projection(
                    scale_x=self.orthographic_scale * aspect_ratio,
                    scale_y=self.orthographic_scale,
                    z_near=self.z_near,
                    z_far=self.z_far)

        # Don't forget to update it inverse
        self.inverse_projection_matrix = np.linalg.inv(self.projection_matrix)

        self.projection_matrix_dirty = False

    def get_projection_matrix(self) -> np.ndarray:

        if self.projection_matrix_dirty:
            self.update_projection_matrix()

        return self.projection_matrix

    def get_inverse_projection_matrix(self) -> np.ndarray:

        if self.projection_matrix_dirty:
            self.update_projection_matrix()

        return self.inverse_projection_matrix
