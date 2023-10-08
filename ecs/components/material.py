from ecs.components.component import Component
from ecs import constants


class Material(Component):

    _type = constants.COMPONENT_TYPE_MESH  # TODO: I think I don't need to set the type as I can use the class itself

    def __init__(self, parameters: dict):
        
        super().__init__(parameters=parameters)

        # Colors
        self.diffuse = Component.dict2color(input_dict=parameters, key="diffuse", default_value=(0.85, 0.85, 0.85))
        self.diffuse_highlight = Component.dict2color(input_dict=parameters,
                                                      key="diffuse_highlight",
                                                      default_value=(0.95, 0.95, 0.95))
        self.specular = Component.dict2color(input_dict=parameters,
                                             key="specular",
                                             default_value=(1.0, 1.0, 1.0))

        # Factors
        self.shininess_factor = Component.dict2float(input_dict=parameters, key="shininess_factor", default_value=32.0)
        self.metalic_factor = Component.dict2float(input_dict=parameters, key="metalic_factor", default_value=0.0)
        self.roughness_factor = Component.dict2float(input_dict=parameters, key="roughness_factor", default_value=1.0)

        # Render modes
        self.color_source = Component.dict2map(input_dict=parameters, key="color_source",
                                               map_dict=constants.COLOR_SOURCE_MAP,
                                               default_value=constants.RENDER_MODE_COLOR_SOURCE_SINGLE)
        self.lighting_mode = Component.dict2map(input_dict=parameters, key="lighting_mode",
                                                map_dict=constants.LIGHTING_MODE_MAP,
                                                default_value=constants.RENDER_MODE_LIGHTING_LIT)

        # Transparency
        self.alpha = Component.dict2float(input_dict=parameters, key="alpha", default_value=1.0)

    def is_transparent(self) -> bool:
        return self.alpha == 1.0
