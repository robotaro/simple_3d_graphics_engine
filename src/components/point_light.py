import numpy as np
import moderngl

from src.core import constants
from src.core.component import Component


class PointLight(Component):

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

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.ubo_index = parameters.get("ubo_index", 0)
        self.ubo_data = np.empty((1,), dtype=PointLight._material_dtype)

        self.ubo_data["position"] = Component.dict2tuple_float(input_dict=self.parameters,
                                                               key="position",
                                                               default_value=(0.0, 0.0, 0.0))
        self.ubo_data["diffuse"] = Component.dict2tuple_float(input_dict=self.parameters,
                                                              key="diffuse",
                                                              default_value=(1.0, 1.0, 1.0))
        self.ubo_data["specular"] = Component.dict2tuple_float(input_dict=self.parameters,
                                                               key="specular",
                                                               default_value=(1.0, 1.0, 1.0))
        self.ubo_data["attenuation_coeffs"] = Component.dict2tuple_float(input_dict=parameters,
                                                                         key="attenuation_coeffs",
                                                                         default_value=(1.0, 0.09, 0.032))
        self.ubo_data["intensity"] = Component.dict2float(input_dict=self.parameters,
                                                          key="intensity",
                                                          default_value=0.8)
        self.ubo_data["enabled"] = Component.dict2bool(input_dict=self.parameters,
                                                       key="enabled",
                                                       default_value=True)

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
