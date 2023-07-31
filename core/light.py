import numpy as np
from core.utilities import utils
from core.node import Node


class Light(Node):
    """Base class for all light objects.

    Parameters
    ----------
    color : (3,) float
        RGB value for the light's color in linear space.
    intensity : float
        Brightness of light. The units that this is defined in depend on the
        type of light. Point and spot lights use luminous intensity in candela
        (lm/sr), while directional lights use illuminance in lux (lm/m2).
    name : str, optional
        Name of the light.
    """
    def __init__(self,
                 name=None,
                 color=None,
                 intensity=None):
        super().__init__(name=name)

        if color is None:
            color = np.ones(3)
        if intensity is None:
            intensity = 1.0

        self._color = color
        self._intensity = intensity
        self._shadow_camera = None
        self._shadow_texture = None


    @property
    def color(self):
        """(3,) float : The light's color.
        """
        return self._color

    @color.setter
    def color(self, value):
        self._color = utils.format_color_vector(value, 3)

    @property
    def intensity(self):
        """float : The light's intensity in candela or lux.
        """
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = float(value)

    @property
    def shadow_texture(self):
        """:class:`.Texture` : A texture used to hold shadow maps for this light.
        """
        return self._shadow_texture

    @shadow_texture.setter
    def shadow_texture(self, value):
        if self._shadow_texture is not None:
            if self._shadow_texture._in_context():
                self._shadow_texture.delete()
        self._shadow_texture = value

    def generate_shadow_texture(self, size=None):
        pass

    def get_shadow_camera(self, scene_scale):
        pass


class DirectionalLight(Light):

    def __init__(self,
                 color=None,
                 intensity=None,
                 name=None):
        super(DirectionalLight, self).__init__(
            color=color,
            intensity=intensity,
            name=name,
        )

    def _generate_shadow_texture(self, size=None):
        """Generate a shadow texture for this light.

        Parameters
        ----------
        size : int, optional
            Size of texture map. Must be a positive power of two.
        """
        """if size is None:
            size = SHADOW_TEX_SZ
        self.shadow_texture = Texture(width=size, height=size,
                                      source_channels='D', data_format=GL_FLOAT)"""
        pass

    def _get_shadow_camera(self, scene_scale):
        """Generate and return a shadow mapping camera for this light.

        Parameters
        ----------
        scene_scale : float
            Length of scene's bounding box diagonal.

        Returns
        -------
        camera : :class:`.Camera`
            The camera used to render shadowmaps for this light.
        """

        # TODO: Return the projection matrix instead?

        """return OrthographicCamera(
            znear=0.01 * scene_scale,
            zfar=10 * scene_scale,
            xmag=scene_scale,
            ymag=scene_scale
        )"""
        pass

__all__ = ['DirectionalLight']
