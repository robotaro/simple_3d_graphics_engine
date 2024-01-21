import numpy as np
import moderngl

from src.core import constants
from src2.components.component import Component
from src2.utilities import utils_params


class Material(Component):

    _type = constants.COMPONENT_TYPE_MESH  # TODO: I think I don't need to set the type as I can use the class itself

    _material_dtype = np.dtype([
        ('diffuse', '3f4'),
        ('color_source', 'i4'),
        ('diffuse_highlight', '3f4'),
        ('lighting_mode', 'i4'),
        ('specular', '3f4'),
        ('padding_0', 'f4'),
        ('shininess_factor', 'f4'),
        ('metalic_factor', 'f4'),
        ('roughness_factor', 'f4'),
        ('padding_1', 'f4')
    ], align=True)

    __slots__ = [
        "ubo_index",
        "ubo_data",
        "diffuse",
        "diffuse_highlight",
        "specular",
        "shininess_factor",
        "metalic_factor",
        "metalic_factor",
        "roughness_factor",
        "color_source",
        "lighting_mode",
        "alpha",
        "state_highlighted",
        "dirty"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ubo_index = self.params.get("ubo_index", 0)
        self.ubo_data = np.empty((1,), dtype=Material._material_dtype)

        self.ubo_data['diffuse'] = utils_params.str2color(self.params.get("diffuse", (0.85, 0.85, 0.85)))
        self.ubo_data['diffuse_highlight'] = utils_params.str2color(self.params.get("diffuse", (0.95, 0.95, 0.95)))
        self.ubo_data['specular'] = utils_params.str2color(self.params.get("specular", (1.0, 1.0, 1.0)))
        self.ubo_data['shininess_factor'] = self.params.get("shininess_factor", 32.0)
        self.ubo_data['metalic_factor'] = self.params.get("metalic_factor", 0.0)
        self.ubo_data['roughness_factor'] = self.params.get("roughness_factor", 1.0)
        self.ubo_data['color_source'] = self.params.get("color_source", constants.RENDER_MODE_COLOR_SOURCE_SINGLE)
        self.ubo_data['lighting_mode'] = constants.LIGHTING_MODE_MAP[self.params.get("lighting_mode", "lit")]
        self.alpha = self.params.get("alpha", 1.0)

        # State Variables - Can be changed by events
        self.state_highlighted = False
        self.dirty = True

    def update_ubo(self, ubo: moderngl.UniformBlock):

        if not self.dirty:
            return

        # Write the data to the UBO
        ubo.write(self.ubo_data.tobytes(), offset=self.ubo_index * constants.SCENE_MATERIAL_STRUCT_SIZE_BYTES)
        self.dirty = False

    def is_transparent(self) -> bool:
        return self.alpha == 1.0

    def draw_imgui_properties(self, imgui):
        imgui.text(f"Material")

        diffuse = tuple(self.ubo_data["diffuse"].flatten())
        a, self.ubo_data["diffuse"][:] = imgui.color_edit3("Material Diffuse", *diffuse)

        diffuse_highlight = tuple(self.ubo_data["diffuse_highlight"].flatten())
        b, self.ubo_data["diffuse_highlight"][:] = imgui.color_edit3("Diffuse Highlight", *diffuse_highlight)

        specular = tuple(self.ubo_data["specular"].flatten())
        c, self.ubo_data["specular"][:] = imgui.color_edit3("Specular", *specular)

        d, self.ubo_data["shininess_factor"] = imgui.drag_float("Shininess Factor",
                                                                self.ubo_data["shininess_factor"],
                                                                0.05,
                                                                0.0,
                                                                32.0,
                                                                "%.3f")

        e, self.ubo_data["color_source"] = imgui.slider_int(
            "Color Source",
            self.ubo_data["color_source"],
            min_value=constants.RENDER_MODE_COLOR_SOURCE_SINGLE,
            max_value=constants.RENDER_MODE_COLOR_SOURCE_UV)

        f, self.ubo_data["lighting_mode"] = imgui.slider_int(
            "Lighting Mode",
            self.ubo_data["lighting_mode"],
            min_value=constants.RENDER_MODE_LIGHTING_SOLID,
            max_value=constants.RENDER_MODE_LIGHTING_LIT)
        self.dirty |= a | b | c | d | e | f
        imgui.spacing()
