import glm
import numpy as np

class Camera:
    def __init__(self, fbo_size, camera_speed=2.5, mouse_sensitivity=0.1):
        self.fbo_size = fbo_size
        aspect_ratio = fbo_size[0] / fbo_size[1]
        self.projection_matrix = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)
        self.view_matrix = glm.inverse(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, 5.0)))

        self.position = glm.vec3(0.0, 1.0, 5.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.speed = camera_speed
        self.sensitivity = mouse_sensitivity
        self.yaw = -90.0
        self.pitch = 0.0

        self.right_mouse_button_down = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.first_mouse = True

        self.key_down_forward = False
        self.key_down_back = False
        self.key_down_left = False
        self.key_down_right = False
        self.key_down_up = False
        self.key_down_down = False

    def process_mouse_movement(self, dx, dy):
        x_offset = dx * self.sensitivity
        y_offset = -dy * self.sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        self.pitch = max(-89.0, min(89.0, self.pitch))

        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

    def process_keyboard(self, elapsed_time):
        factor = self.speed * elapsed_time

        if self.key_down_forward:
            self.position += factor * self.front
        if self.key_down_back:
            self.position -= factor * self.front
        if self.key_down_up:
            self.position += factor * glm.vec3(0, 1, 0)
        if self.key_down_down:
            self.position -= factor * glm.vec3(0, 1, 0)
        if self.key_down_left:
            self.position -= glm.normalize(glm.cross(self.front, self.up)) * factor
        if self.key_down_right:
            self.position += glm.normalize(glm.cross(self.front, self.up)) * factor

        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.up)

    def handle_key_press(self, key):
        if key == ord('W') or key == ord('w'):
            self.key_down_forward = True
        if key == ord('S') or key == ord('s'):
            self.key_down_back = True
        if key == ord('A') or key == ord('a'):
            self.key_down_left = True
        if key == ord('D') or key == ord('d'):
            self.key_down_right = True
        if key == ord('E') or key == ord('e'):
            self.key_down_up = True
        if key == ord('Q') or key == ord('q'):
            self.key_down_down = True

    def handle_key_release(self, key):
        if key == ord('W') or key == ord('w'):
            self.key_down_forward = False
        if key == ord('S') or key == ord('s'):
            self.key_down_back = False
        if key == ord('A') or key == ord('a'):
            self.key_down_left = False
        if key == ord('D') or key == ord('d'):
            self.key_down_right = False
        if key == ord('E') or key == ord('e'):
            self.key_down_up = False
        if key == ord('Q') or key == ord('q'):
            self.key_down_down = False
