from typing import Tuple
import numpy as np

from core.scene.cameras.main_camera import MainCamera
from core.scene.cameras.camera_interface import CameraInterface


class Viewport:
    def __init__(self, extents: Tuple[int, int, int, int], camera: CameraInterface):
        self.extents = extents
        self._camera = camera
        self._using_temp_camera = not isinstance(camera, MainCamera)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera: CameraInterface):
        self._camera = camera
        self._using_temp_camera = not isinstance(camera, MainCamera)

    def contains(self, x: int, y: int) -> bool:
        """
        Check if point is contained inside this viewport
        :param x: int, X screen coordinate
        :param y: int, Y screen coordinate
        :return:
        """
        e = self.extents
        return x >= e[0] and x < e[0] + e[2] and y >= e[1] and y < e[1] + e[3]

    def set_temp_camera(self, camera: CameraInterface):
        self.camera = camera
        self._using_temp_camera = True

    def reset_camera(self):
        if not self._using_temp_camera:
            return

        self._using_temp_camera = False

        fwd = self.camera.forward
        pos = self.camera.position

        self.camera = MainCamera(45)
        self.camera.position = np.copy(pos)
        self.camera.target = pos + fwd * 3
        self.camera.update_matrices(*self.extents[2:])
