import numpy as np
import moderngl

from src.core import constants
from src.core.component import Component


class Material(Component):

    _type = constants.COMPONENT_TYPE_MESH  # TODO: I think I don't need to set the type as I can use the class itself

    _material_dtype = np.dtype([
        ('diffuse', '4f4'),
        ('ambient', '4f4'),
        ('specular', '4f4'),
        ('shininess_factor', 'f4'),
        ('metalic_factor', 'f4'),
        ('roughness_factor', 'f4'),
        ('padding', 'f4')  # Padding to align to vec4
    ], align=True)

    __slots__ = [
        "ubo_index",
        "material_data",
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

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        # TODO: Make this official
        self.ubo_index = parameters.get("ubo_index", 0)
        self.material_data = np.empty((1, ), dtype=Material._material_dtype)

        # Colors
        self.diffuse = Component.dict2color(input_dict=self.parameters, key="diffuse", default_value=(0.85, 0.85, 0.85))
        self.diffuse_highlight = Component.dict2color(input_dict=self.parameters,
                                                      key="diffuse_highlight",
                                                      default_value=(0.95, 0.95, 0.95))
        self.specular = Component.dict2color(input_dict=self.parameters,
                                             key="specular",
                                             default_value=(1.0, 1.0, 1.0))
        self.shininess_factor = Component.dict2float(input_dict=self.parameters,
                                                     key="shininess_factor",
                                                     default_value=32.0)
        self.metalic_factor = Component.dict2float(input_dict=self.parameters,
                                                   key="metalic_factor",
                                                   default_value=0.0)
        self.roughness_factor = Component.dict2float(input_dict=self.parameters,
                                                     key="roughness_factor",
                                                     default_value=1.0)

        # Render modes
        self.color_source = Component.dict2map(input_dict=self.parameters, key="color_source",
                                               map_dict=constants.COLOR_SOURCE_MAP,
                                               default_value=constants.RENDER_MODE_COLOR_SOURCE_SINGLE)
        self.lighting_mode = Component.dict2map(input_dict=self.parameters, key="lighting_mode",
                                                map_dict=constants.LIGHTING_MODE_MAP,
                                                default_value=constants.RENDER_MODE_LIGHTING_LIT)
        self.alpha = Component.dict2float(input_dict=self.parameters, key="alpha", default_value=1.0)

        # State Variables - Can be changed by events
        self.state_highlighted = False
        self.dirty = True

    def update_ubo(self, material_ubo: moderngl.UniformBlock):

        if not self.dirty:
            return

        # TODO: This only needs to up updated
        self.material_data['diffuse'] = (*self.diffuse, 0)
        self.material_data['ambient'] = (0, 0, 0, 0)
        self.material_data['specular'] = (*self.specular, 0)

        # Write the data to the UBO
        material_ubo.write(self.material_data.tobytes(),
                           offset=self.ubo_index * constants.SCENE_MATERIAL_STRUCT_SIZE_BYTES)
        self.dirty = False

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
