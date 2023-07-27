
class Material:

    __slots__ = ["_diffuse",
                 "_ambient",
                 "_specular",
                 "_color",
                 "_alpha"]

    def __init__(
        self,
        diffuse=0.5,
        ambient=0.5,
        specular=0.5,
        alpha=1.0,
        color_rgb=(0.5, 0.5, 0.5),
    ):
        """
        :param diffuse: diffuse coefficient in Phong shading model
        :param ambient: ambient coefficient in Phong shading model
        :param specular: specular coefficient in Phong shading model
        :param color_rgb: (R,G,B) 0-1 formatted color value
        """

        self._diffuse = diffuse
        self._ambient = ambient
        self._specular = specular
        self._color = color_rgb
        self._alpha = alpha

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        # TODO: No checks for alpha <= 0.0. Change this later
        self._alpha = value if value <= 1.0 else 1.0

    @property
    def is_transparent(self):
        return self._alpha == 1.0