import os
from abc import ABC, abstractmethod
import numpy as np
from trimesh.transformations import rotation_matrix

from core.settings import SETTINGS
from core import constants
from core.utilities import utils_camera


def _transform_vector(transform, vector):
    """Apply affine transformation (4-by-4 matrix) to a 3D vector."""
    return (transform @ np.concatenate([vector, np.array([1])]))[:3]


def _transform_direction(transform, vector):
    """Apply affine transformation (4-by-4 matrix) to a 3D directon."""
    return (transform @ np.concatenate([vector, np.array([0])]))[:3]


class CameraInterface(ABC):
    """
    An abstract class which describes the interface expected by the viewer for using this object as a camera
    """

    def __init__(self):
        self.projection_matrix = None
        self.view_matrix = None
        self.view_projection_matrix = None

    def get_projection_matrix(self):
        if self.projection_matrix is None:
            raise ValueError("update_matrices() must be called before to update the projection matrix")
        return self.projection_matrix

    def get_view_matrix(self):
        if self.view_matrix is None:
            raise ValueError("update_matrices() must be called before to update the view matrix")
        return self.view_matrix

    def get_view_projection_matrix(self):
        if self.view_projection_matrix is None:
            raise ValueError("update_matrices() must be called before to update the view-projection matrix")
        return self.view_projection_matrix

    @abstractmethod
    def update_matrices(self, width, height):
        pass

    @property
    @abstractmethod
    def position(self):
        pass

    @property
    @abstractmethod
    def forward(self):
        pass

    @property
    @abstractmethod
    def up(self):
        pass

    @property
    @abstractmethod
    def right(self):
        pass

    def gui(self, imgui):
        pass
