



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
