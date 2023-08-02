import numpy as np
import moderngl
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


class DirectionalLight:

    __slots__ = [
        "name",
        "direction",
        "intensity",
        "color"
    ]

    def __init__(self,
                 name: str,
                 color=(1.0, 1.0, 1.0),
                 direction=(-1.0, -1.0, -1.0),
                 intensity=1.0):

        self.name = name
        self.color = color
        self.direction = np.array(direction)
        self.direction /= np.linalg.norm(self.direction)
        self.intensity = intensity

    def upload_uniforms(self, light_index: int, program: moderngl.Program):


        prog[f"dirLights[{i}].direction"].value = tuple(light.direction)
        prog[f"dirLights[{i}].color"].value = light.light_color
        prog[f"dirLights[{i}].strength"].value = light.strength if light.enabled else 0.0
        prog[f"dirLights[{i}].shadow_enabled"].value = shadows_enabled and light.shadow_enabled



    def generate_shadow_texture(self, size=None):

        pass

    def get_shadow_camera(self, scene_scale):
        pass

__all__ = ['DirectionalLight']
