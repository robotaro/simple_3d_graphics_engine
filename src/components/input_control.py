import numpy as np

from src.core.component import Component


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

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.active = True
        self.mouse_sensitivity = Component.dict2float(input_dict=self.parameters,
                                                      key="mouse_sensitivity",
                                                      default_value=0.01)
        self.speed = Component.dict2float(input_dict=self.parameters, key="speed", default_value=1.0)
        self.max_tilt = 0.4
        self.pitch = 0.0
        self.yaw = 0.0
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.forward = np.array([0, 0, 1], dtype=np.float32)
