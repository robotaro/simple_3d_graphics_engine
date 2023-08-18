import numpy as np

from ecs import constants
from ecs.components.component import Component


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
        "pitch"     # In radians
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.active = True
        self.mouse_sensitivity = kwargs.get("mouse_sensitivity", 0.01)
        self.speed = kwargs.get("speed", 0.1)
        self.max_tilt = 0.4
        self.pitch = 0.0
        self.yaw = 0.0
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.forward = np.array([0, 0, 1], dtype=np.float32)
