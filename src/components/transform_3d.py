import numpy as np

from src.core import constants
from src.components.component import Component


class Transform3D(Component):

    _type = "transform"

    __slots__ = [
        "local_matrix",
        "world_matrix",
        "position",
        "rotation",
        "scale",
        "degrees",
        "dirty"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.position = Component.dict2tuple_float(input_dict=self.parameters,
                                                   key="position",
                                                   default_value=(0.0, 0.0, 0.0))
        self.rotation = Component.dict2tuple_float(input_dict=self.parameters,
                                                   key="rotation",
                                                   default_value=(0.0, 0.0, 0.0))
        self.scale = Component.dict2float(input_dict=self.parameters,
                                          key="scale",
                                          default_value=1.0)
        self.degrees = Component.dict2bool(input_dict=self.parameters,
                                           key="degrees",
                                           default_value=False)

        if self.degrees:
            self.rotation = (self.rotation[0] * constants.DEG2RAD,
                             self.rotation[1] * constants.DEG2RAD,
                             self.rotation[2] * constants.DEG2RAD)

        self.local_matrix = np.eye(4, dtype=np.float32)
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.dirty = True

    def move(self, delta_position: np.array):
        self.position += delta_position
        self.dirty = True

    def rotate(self, delta_rotation: np.array):
        self.rotation += delta_rotation
        self.dirty = True

    def set_position(self, position: tuple):
        self.position = position
        self.dirty = True

    def set_rotation(self, position: tuple):
        self.position = position
        self.dirty = True
