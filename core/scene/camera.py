import numpy as np
from core import constants
from core.scene.node import Node


class Camera(Node):

    def __init__(self,
                 znear=constants.CAMERA_Z_NEAR,
                 zfar=constants.CAMERA_Z_FAR,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.znear = znear
        self.zfar = zfar

    @property
    def name(self):
        """str : The user-defined name of this object.
        """
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            value = str(value)
        self._name = value

    @property
    def znear(self):
        """float : The distance to the near clipping plane.
        """
        return self._znear

    @znear.setter
    def znear(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('z-near must be >= 0.0')
        self._znear = value

    @property
    def zfar(self):
        """float : The distance to the far clipping plane.
        """
        return self._zfar

    @zfar.setter
    def zfar(self, value):
        value = float(value)
        if value <= 0 or value <= self.znear:
            raise ValueError('zfar must be >0 and >znear')
        self._zfar = value

    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """
        pass
