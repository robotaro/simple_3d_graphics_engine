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

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.z_near = self.dict2float(input_dict=self.parameters, key="z_near", default_value=constants.CAMERA_Z_NEAR)
        self.z_far = self.dict2float(input_dict=self.parameters, key="z_far", default_value=constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # Orthographic variables
        self.orthographic_scale = 1.0
        self.viewport_ratio = self.dict2tuple_float(input_dict=self.parameters, key="viewport_ratio",
                                                    default_value=(0.0, 0.0, 1.0, 1.0))
        self.viewport_pixels = None

        # Flags
        self.perspective = self.dict2bool(input_dict=self.parameters, key="perspective", default_value=True)

    def upload_uniforms(self, program: moderngl.Program):
        program["projection_matrix"].write(self.get_projection_matrix().T.tobytes())

    def update_viewport(self, window_size: tuple):

        self.viewport_pixels = (int(self.viewport_ratio[0] * window_size[0]),
                                int(self.viewport_ratio[1] * window_size[1]),
                                int(self.viewport_ratio[2] * window_size[0]),
                                int(self.viewport_ratio[3] * window_size[1]))

    def is_inside_viewport(self, coord_pixels: tuple) -> bool:
        if self.viewport_pixels is None:
            return False

        flag_x = self.viewport_pixels[0] <= coord_pixels[0] < (self.viewport_pixels[2] + self.viewport_pixels[0])
        flag_y = self.viewport_pixels[1] <= coord_pixels[1] < (self.viewport_pixels[3] + self.viewport_pixels[1])

        return flag_x & flag_y

    def get_ray(self, screen_coord_pixels: tuple) -> Union[tuple, None]:

        if screen_coord_pixels is None:
            return None

    def get_viewport_coordinates(self, screen_coord_pixels: tuple) -> Union[tuple, None]:
        """
        Returns a normalised coordinates withing the viewport of the camera. This will return
        erroneous values if the input coordinates are outside the viewport in screen values
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

    def get_projection_matrix(self):

        aspect_ratio = self.viewport_pixels[2] / self.viewport_pixels[3]

        if self.perspective:
            return utils_camera.perspective_projection(
                fov_rad=self.y_fov_deg * constants.DEG2RAD,
                aspect_ratio=aspect_ratio,
                z_near=self.z_near,
                z_far=self.z_far)
        else:
            return utils_camera.orthographic_projection(
                scale_x=self.orthographic_scale * aspect_ratio,
                scale_y=self.orthographic_scale,
                z_near=self.z_near,
                z_far=self.z_far)

