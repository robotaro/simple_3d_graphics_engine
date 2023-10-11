import numpy as np
import moderngl
from typing import Union

from src import constants
from src.components.component import Component
from src.utilities import utils_camera


class Camera(Component):

    _type = "camera"

    __slots__ = [
        "y_fov_deg",
        "z_near",
        "z_far",
        "orthographic_scale",
        "viewport_ratio",
        "viewport_pixels",
        "perspective"
    ]

    def __init__(self, parameters: dict):

        if parameters is None:
            parameters = {}

        super().__init__(parameters=parameters)

        self.z_near = self.dict2float(input_dict=parameters, key="z_near", default_value=constants.CAMERA_Z_NEAR)
        self.z_far = self.dict2float(input_dict=parameters, key="z_far", default_value=constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # Orthographic variables
        self.orthographic_scale = 1.0
        self.viewport_ratio = self.dict2tuple_float(input_dict=parameters, key="viewport_ratio",
                                                    default_value=(0.0, 0.0, 1.0, 1.0))
        self.viewport_pixels = None

        # Flags
        self.perspective = self.dict2bool(input_dict=parameters, key="perspective", default_value=True)

    def upload_uniforms(self, program: moderngl.Program, window_width: int, window_height: int):
        proj_matrix_bytes = self.get_projection_matrix(window_width=window_width,
                                                       window_height=window_height).T.tobytes()
        program["projection_matrix"].write(proj_matrix_bytes)

    def update_viewport(self, window_size: tuple):
        self.viewport_pixels = (int(self.viewport_ratio[0] * window_size[0]),
                                int(self.viewport_ratio[1] * window_size[1]),
                                int(self.viewport_ratio[2] * window_size[0]),
                                int(self.viewport_ratio[3] * window_size[1]))

    def is_inside_viewport(self, coord_pixels: tuple) -> bool:
        if self.viewport_pixels is None:
            return False

        flag_x = self.viewport_pixels[0] <= coord_pixels[0] < self.viewport_pixels[2] + self.viewport_pixels[0]
        flag_y = self.viewport_pixels[1] <= coord_pixels[1] < self.viewport_pixels[3] + self.viewport_pixels[1]

        return flag_x & flag_y

    def get_viewport_coordinates(self, screen_coord_pixels: tuple) -> Union[tuple, None]:
        """
        Returns a normalised coordinates withing the viewport of the camera. This will return
        errouneous values if the input coordinates are outside the viewport in screen values
        """
        if self.viewport_pixels is None:
            return None

        # Get normalise values
        x = (screen_coord_pixels[0] - self.viewport_pixels[0]) / self.viewport_pixels[2]
        y = (screen_coord_pixels[1] - self.viewport_pixels[1]) / self.viewport_pixels[3]

        # Convert normalised values to viewport coordinates (-1 to 1)
        x = 2.0 * x - 1.0
        y = 2.0 * y - 1.0

        return x, y

    def get_projection_matrix(self, window_width: int, window_height: int):

        nom = window_width * (self.viewport_ratio[2] - self.viewport_ratio[0])
        den = window_height * (self.viewport_ratio[3] - self.viewport_ratio[1])
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

