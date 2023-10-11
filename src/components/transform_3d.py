import numpy as np

from src import constants
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

    def __init__(self, parameters: dict):
        super().__init__(parameters=parameters)

        self.position = Component.dict2tuple_float(input_dict=parameters, key="position", default_value=(0.0, 0.0, 0.0))
        self.rotation = Component.dict2tuple_float(input_dict=parameters, key="rotation", default_value=(0.0, 0.0, 0.0))
        self.scale = Component.dict2tuple_float(input_dict=parameters, key="scale", default_value=(1.0, 1.0, 1.0))
        self.degrees = Component.dict2bool(input_dict=parameters, key="degrees", default_value=False)

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
