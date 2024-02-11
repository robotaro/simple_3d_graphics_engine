import numpy as np
import moderngl

from src.core import constants
from src2.entities.entity import Entity
from src2.utilities import utils_params


class PointLight(Entity):

    __slots__ = [
        "ubo_index",
        "ubo_data",
        "diffuse",
        "ambient",
        "specular",
        "intensity",
        "attenuation_coeffs",
        "enabled",
        "dirty"
    ]

    _type = constants.COMPONENT_TYPE_SPOT_LIGHT

    _material_dtype = np.dtype([
        ('position', '3f4'),
        ('padding_0', 'f4'),
        ('diffuse', '3f4'),
        ('intensity', 'f4'),
        ('specular', '3f4'),
        ('enabled', 'f4'),
        ('attenuation_coeffs', '3f4'),
        ('padding_1', 'f4'),
    ], align=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ubo_index = self.params.get("ubo_index", 0)
        self.ubo_data = np.empty((1,), dtype=PointLight._material_dtype)
        self.ubo_data["position"] = self.params.get("position", (0.0, 0.0, 0.0))
        self.ubo_data["diffuse"] = utils_params.str2color(self.params.get("diffuse", (1.0, 1.0, 1.0)))
        self.ubo_data["specular"] = utils_params.str2color(self.params.get("specular", (1.0, 1.0, 1.0)))
        self.ubo_data["attenuation_coeffs"] = self.params.get("attenuation_coeffs", (1.0, 0.09, 0.032))
        self.ubo_data["intensity"] = self.params.get("intensity", 0.8)
        self.ubo_data["enabled"] = self.params.get("enabled", True)

        self.dirty = True

    def update_ubo(self, ubo: moderngl.UniformBlock):

        if not self.dirty:
            return

        # Write the data to the UBO
        ubo.write(self.ubo_data.tobytes(), offset=self.ubo_index * constants.SCENE_POINT_LIGHT_STRUCT_SIZE_BYTES)
        self.dirty = False

    def draw_imgui_properties(self, imgui):
        imgui.text(f"Point Light")

        position = tuple(self.ubo_data["position"].flatten())
        a, self.ubo_data["position"][:] = imgui.drag_float3("Light Position",
                                                            *position,
                                                            0.005,
                                                            -1000.0,
                                                            1000.0,
                                                            "%.3f")

        diffuse = tuple(self.ubo_data["diffuse"].flatten())
        b, self.ubo_data["diffuse"][:] = imgui.color_edit3("Light Diffuse", *diffuse)

        specular = tuple(self.ubo_data["specular"].flatten())
        c, self.ubo_data["specular"][:] = imgui.color_edit3("Light Specular", *specular)

        attenuation_coeffs = tuple(self.ubo_data["attenuation_coeffs"].flatten())
        d, self.ubo_data["attenuation_coeffs"][:] = imgui.drag_float3("Attenuation Coeffs.",
                                                                      *attenuation_coeffs,
                                                                      0.005,
                                                                      0.0,
                                                                      100.0,
                                                                      "%.3f")
        self.dirty |= a | b | c | d

        imgui.spacing()
