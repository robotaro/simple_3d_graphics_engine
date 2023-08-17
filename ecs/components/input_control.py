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

    def rotate(self, dx: float, dy: float):
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        self.pitch = np.clip(self.pitch, -np.pi * 0.49, np.pi * 0.49)

    def update_camera_vectors(self):

        self.forward.x = np.cos(self.yaw) * np.cos(self.pitch)
        self.forward.y = np.sin(self.pitch)
        self.forward.z = np.sin(self.yaw) * np.cos(self.pitch)

        self.forward = np.linalg.norm(self.forward)
        self.right = np.linalg.norm(np.cross(self.forward, np.array((0, 1, 0))))
        self.up = np.linalg.norm(np.cross(self.right, self.forward))

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self, delta_time: float):
        velocity = self.speed * delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * self.speed
        if keys[pg.K_s]:
            self.position -= self.forward * self.speed
        if keys[pg.K_a]:
            self.position -= self.right * self.speed
        if keys[pg.K_d]:
            self.position += self.right * self.speed
        if keys[pg.K_q]:
            self.position += self.up * self.speed
        if keys[pg.K_e]:
            self.position -= self.up * self.speed