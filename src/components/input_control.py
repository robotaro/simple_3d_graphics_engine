import numpy as np

from src import constants
from src.components.component import Component


class InputControl(Component):

    _type = "input_control"

    __slots__ = [
        "active",
        "mouse_sensitivity",
        "speed",
        "position",
        "forward",
        "right",
        "up",
        "yaw",      # In radians
        "pitch",     # In radians
        "max_tilt"
    ]

    def __init__(self, parameters: dict):
        super().__init__(parameters=parameters)

        self.active = True
        self.mouse_sensitivity = Component.dict2float(input_dict=parameters,
                                                      key="mouse_sensitivity",
                                                      default_value=0.01)
        self.speed = Component.dict2float(input_dict=parameters, key="speed", default_value=0.1)
        self.max_tilt = 0.4
        self.pitch = 0.0
        self.yaw = 0.0
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.forward = np.array([0, 0, 1], dtype=np.float32)
