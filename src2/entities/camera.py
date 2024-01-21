import numpy as np

from src.core import constants
from src.utilities import utils_camera
from src2.entities.entity import Entity
from src2.utilities import utils_params


class Camera(Entity):

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.z_near = self.params.get("z_near", constants.CAMERA_Z_NEAR)
        self.z_far = self.params.get("z_far", constants.CAMERA_Z_FAR)

        # Perspective variables
        self.y_fov_deg = constants.CAMERA_FOV_DEG

        # Orthographic variables
        self.orthographic_scale = 1.0

        # Flags
        self.is_perspective = self.params.get("perspective", True)

        # Projection Matrix
        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.inverse_projection_matrix = np.eye(4, dtype=np.float32)
        self.projection_matrix_dirty = True

    def update_projection_matrix(self, viewport_pixels: tuple):

        aspect_ratio = viewport_pixels[2] / viewport_pixels[3]
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

    def draw_imgui_properties(self, imgui):
        imgui.text(f"Camera")
        _, self.is_perspective = imgui.checkbox("Perspective", self.is_perspective)
        imgui.spacing()
