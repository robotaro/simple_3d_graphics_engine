from core import constants
from core.node import Node


class Camera(Node):

    _type = "camera"

    def __init__(self,
                 z_near=constants.CAMERA_Z_NEAR,
                 z_far=constants.CAMERA_Z_FAR,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._z_near = z_near
        self._z_far = z_far

    @property
    def z_near(self):
        """float : The distance to the near clipping plane.
        """
        return self._znear

    @z_near.setter
    def z_near(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('z-near must be >= 0.0')
        self._z_near = value

    @property
    def z_far(self):
        """float : The distance to the far clipping plane.
        """
        return self.zfar

    @z_far.setter
    def zfar(self, value):
        value = float(value)
        if value <= 0 or value <= self.znear:
            raise ValueError('zfar must be >0 and >znear')
        self.zfar = value

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
