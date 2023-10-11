import numpy as np

from ecs import constants
from ecs.components.component import Component


class PointLight(Component):

    __slots__ = [
        "diffuse",
        "ambient",
        "specular",
        "intensity",
        "attenuation_coeffs",
        "enabled"
    ]

    _type = constants.COMPONENT_TYPE_SPOT_LIGHT

    def __init__(self, parameters):
        super().__init__(parameters=parameters)

        self.diffuse = Component.dict2tuple_float(input_dict=parameters, key="diffuse", default_value=(1.0, 1.0, 1.0))
        self.specular = Component.dict2tuple_float(input_dict=parameters, key="specular", default_value=(1.0, 1.0, 1.0))

        self.attenuation_coeffs = Component.dict2tuple_float(input_dict=parameters,
                                                             key="attenuation_coeffs",
                                                             default_value=(1.0, 0.09, 0.032))

        self.intensity = Component.dict2float(input_dict=parameters, key="intensity", default_value=0.8)
        self.enabled = Component.dict2bool(input_dict=parameters, key="enabled", default_value=True)

