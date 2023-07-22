import numpy as np
from core.utilities import utils

# TODO: Make this an interface light
class Light(object):
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

        if color is None:
            color = np.ones(3)
        if intensity is None:
            intensity = 1.0

        self.name = name
        self.color = color
        self.intensity = intensity
        self._shadow_camera = None
        self._shadow_texture = None

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
        """Generate a shadow texture for this light.

        Parameters
        ----------
        size : int, optional
            Size of texture map. Must be a positive power of two.
        """
        pass

    def get_shadow_camera(self, scene_scale):
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
        pass


class DirectionalLight(Light):
    """Directional lights are light sources that act as though they are
    infinitely far away and emit light in the direction of the local -z axis.
    This light type inherits the orientation of the node that it belongs to;
    position and scale are ignored except for their effect on the inherited
    node orientation. Because it is at an infinite distance, the light is
    not attenuated. Its intensity is defined in lumens per metre squared,
    or lux (lm/m2).

    Parameters
    ----------
    color : (3,) float, optional
        RGB value for the light's color in linear space. Defaults to white
        (i.e. [1.0, 1.0, 1.0]).
    intensity : float, optional
        Brightness of light, in lux (lm/m^2). Defaults to 1.0
    name : str, optional
        Name of the light.
    """

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
        if size is None:
            size = SHADOW_TEX_SZ
        self.shadow_texture = Texture(width=size, height=size,
                                      source_channels='D', data_format=GL_FLOAT)

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
        return OrthographicCamera(
            znear=0.01 * scene_scale,
            zfar=10 * scene_scale,
            xmag=scene_scale,
            ymag=scene_scale
        )


class PointLight(Light):
    """Point lights emit light in all directions from their position in space;
    rotation and scale are ignored except for their effect on the inherited
    node position. The brightness of the light attenuates in a physically
    correct manner as distance increases from the light's position (i.e.
    brightness goes like the inverse square of the distance). Point light
    intensity is defined in candela, which is lumens per square radian (lm/sr).

    Parameters
    ----------
    color : (3,) float
        RGB value for the light's color in linear space.
    intensity : float
        Brightness of light in candela (lm/sr).
    range : float
        Cutoff distance at which light's intensity may be considered to
        have reached zero. If None, the range is assumed to be infinite.
    name : str, optional
        Name of the light.
    """

    def __init__(self,
                 color=None,
                 intensity=None,
                 range=None,
                 name=None):
        super(PointLight, self).__init__(
            color=color,
            intensity=intensity,
            name=name,
        )
        self.range = range

    @property
    def range(self):
        """float : The cutoff distance for the light.
        """
        return self._range

    @range.setter
    def range(self, value):
        if value is not None:
            value = float(value)
            if value <= 0:
                raise ValueError('Range must be > 0')
            self._range = value
        self._range = value

    def _generate_shadow_texture(self, size=None):
        """Generate a shadow texture for this light.

        Parameters
        ----------
        size : int, optional
            Size of texture map. Must be a positive power of two.
        """
        raise NotImplementedError('Shadows not implemented for point lights')

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
        raise NotImplementedError('Shadows not implemented for point lights')


__all__ = ['Light', 'DirectionalLight', 'PointLight']
