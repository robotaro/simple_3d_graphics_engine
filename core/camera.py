import numpy as np

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
        return self._z_near

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
        return self._z_far

    @z_far.setter
    def z_far(self, value):
        value = float(value)
        if value <= 0 or value <= self._z_near:
            raise ValueError('zfar must be >0 and >znear')
        self._z_far = value

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


class PerspectiveCamera(Camera):

    """A perspective camera for perspective projection.

    Parameters
    ----------
    y_fov_deg : float
        The floating-point vertical field of view in radians.
    znear : float
        The floating-point distance to the near clipping plane.
        If not specified, defaults to 0.05.
    zfar : float, optional
        The floating-point distance to the far clipping plane.
        ``zfar`` must be greater than ``znear``.
        If None, the camera uses an infinite projection matrix.
    aspect_ratio : float, optional
        The floating-point aspect ratio of the field of view.
        If not specified, the camera uses the viewport's aspect ratio.
    name : str, optional
        The user-defined name of this object.
    """

    def __init__(self,
                 y_fov_deg,
                 z_near=constants.CAMERA_Z_NEAR,
                 z_far=constants.CAMERA_Z_FAR,
                 aspect_ratio=None,
                 **kwargs):
        super(PerspectiveCamera, self).__init__(
            z_near=z_near,
            z_far=z_far,
            **kwargs
        )

        self.y_fov_deg = y_fov_deg
        self.aspect_ratio = aspect_ratio

    @property
    def y_fov_deg(self):
        """float : The vertical field of view in radians.
        """
        return self._yfov

    @y_fov_deg.setter
    def y_fov_deg(self, value):
        value = float(value)
        if value <= 0.0:
            raise ValueError('Field of view must be positive')
        self._yfov = value

    @property
    def aspect_ratio(self):
        """float : The ratio of the width to the height of the field of view.
        """
        return self._aspectRatio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        if value is not None:
            value = float(value)
            if value <= 0.0:
                raise ValueError('Aspect ratio must be positive')
        self._aspectRatio = value

    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """
        aspect_ratio = self.aspect_ratio
        if aspect_ratio is None:
            if width is None or height is None:
                raise ValueError('Aspect ratio of camera must be defined')
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


class OrthographicCamera(Camera):
    """An orthographic camera for orthographic projection.

    Parameters
    ----------
    x_mag : float
        The floating-point horizontal magnification of the view.
    y_mag : float
        The floating-point vertical magnification of the view.
    z_near : float
        The floating-point distance to the near clipping plane.
        If not specified, defaults to 0.05.
    zfar : float
        The floating-point distance to the far clipping plane.
        ``zfar`` must be greater than ``znear``.
        If not specified, defaults to 100.0.
    name : str, optional
        The user-defined name of this object.
    """

    def __init__(self,
                 x_mag,
                 y_mag,
                 z_near=constants.CAMERA_Z_NEAR,
                 z_far=constants.CAMERA_Z_FAR):
        super(OrthographicCamera, self).__init__(
            z_near=z_near,
            z_far=z_far
        )

        self.x_mag = x_mag
        self.y_mag = y_mag

    @property
    def x_mag(self):
        """float : The horizontal magnification of the view.
        """
        return self._xmag

    @x_mag.setter
    def x_mag(self, value):
        value = float(value)
        if value <= 0.0:
            raise ValueError('X magnification must be positive')
        self._xmag = value

    @property
    def y_mag(self):
        """float : The vertical magnification of the view.
        """
        return self._ymag

    @y_mag.setter
    def y_mag(self, value):
        value = float(value)
        if value <= 0.0:
            raise ValueError('Y magnification must be positive')
        self._ymag = value

    @property
    def znear(self):
        """float : The distance to the near clipping plane.
        """
        return self._znear

    @znear.setter
    def znear(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError('z-near must be > 0.0')
        self._znear = value

    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
            Unused in this function.
        height : int
            Height of the current viewport, in pixels.
            Unused in this function.
        """
        xmag = self.x_mag
        ymag = self.y_mag

        # If screen width/height defined, rescale xmag
        if width is not None and height is not None:
            xmag = width / height * ymag

        n = self.znear
        f = self.zfar
        P = np.zeros((4,4))
        P[0][0] = 1.0 / xmag
        P[1][1] = 1.0 / ymag
        P[2][2] = 2.0 / (n - f)
        P[2][3] = (f + n) / (n - f)
        P[3][3] = 1.0
        return P




__all__ = ['Camera', 'PerspectiveCamera', 'OrthographicCamera']
