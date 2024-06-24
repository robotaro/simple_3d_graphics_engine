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

        self.key_map = {
            ord('W'): 'key_down_forward',
            ord('w'): 'key_down_forward',
            ord('S'): 'key_down_back',
            ord('s'): 'key_down_back',
            ord('A'): 'key_down_left',
            ord('a'): 'key_down_left',
            ord('D'): 'key_down_right',
            ord('d'): 'key_down_right',
            ord('E'): 'key_down_up',
            ord('e'): 'key_down_up',
            ord('Q'): 'key_down_down',
            ord('q'): 'key_down_down'
        }

        self.key_states = {
            'key_down_forward': False,
            'key_down_back': False,
            'key_down_left': False,
            'key_down_right': False,
            'key_down_up': False,
            'key_down_down': False
        }

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

        if self.key_states['key_down_forward']:
            self.position += factor * self.front
        if self.key_states['key_down_back']:
            self.position -= factor * self.front
        if self.key_states['key_down_up']:
            self.position += factor * glm.vec3(0, 1, 0)
        if self.key_states['key_down_down']:
            self.position -= factor * glm.vec3(0, 1, 0)
        if self.key_states['key_down_left']:
            self.position -= glm.normalize(glm.cross(self.front, self.up)) * factor
        if self.key_states['key_down_right']:
            self.position += glm.normalize(glm.cross(self.front, self.up)) * factor

        self.view_matrix = glm.lookAt(self.position, self.position + self.front, self.up)

    def handle_key_press(self, key):
        if key in self.key_map:
            self.key_states[self.key_map[key]] = True

    def handle_key_release(self, key):
        if key in self.key_map:
            self.key_states[self.key_map[key]] = False

    def toggle_right_mouse_button(self, state):
        self.right_mouse_button_down = state
