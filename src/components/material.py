from src import constants
from src.components.component import Component


class Material(Component):

    _type = constants.COMPONENT_TYPE_MESH  # TODO: I think I don't need to set the type as I can use the class itself

    __slots__ = [
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
        "state_highlighted"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        # Colors
        self.diffuse = Component.dict2color(input_dict=self.parameters, key="diffuse", default_value=(0.85, 0.85, 0.85))
        self.diffuse_highlight = Component.dict2color(input_dict=self.parameters,
                                                      key="diffuse_highlight",
                                                      default_value=(0.95, 0.95, 0.95))
        self.specular = Component.dict2color(input_dict=self.parameters,
                                             key="specular",
                                             default_value=(1.0, 1.0, 1.0))
        self.shininess_factor = Component.dict2float(input_dict=self.parameters, key="shininess_factor", default_value=32.0)
        self.metalic_factor = Component.dict2float(input_dict=self.parameters, key="metalic_factor", default_value=0.0)
        self.roughness_factor = Component.dict2float(input_dict=self.parameters, key="roughness_factor", default_value=1.0)

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

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
