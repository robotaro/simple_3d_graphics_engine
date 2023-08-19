import glfw
import moderngl
import numpy as np

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool


class InputControlSystem(System):

    _type = "input_control_system"

    __slots__ = [
        "mouse_x_past",
        "mouse_y_past",
        "mouse_dx",
        "mouse_dy",
        "move_forward",
        "move_back",
        "move_left",
        "move_right",
        "move_up",
        "move_down",
        "tilt_up",
        "tilt_down",
        "pan_left",
        "pan_right"
    ]

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"])

        self.mouse_x_past = None
        self.mouse_y_past = None
        self.mouse_dx = 0
        self.mouse_dy = 0

        # Commands
        self.move_forward = False
        self.move_back = False
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.tilt_up = False
        self.tilt_down = False
        self.pan_left = False
        self.pan_right = False

    def initialise(self, **kwargs) -> bool:
        return True

    def update(self,
               elapsed_time: float,
               component_pool: ComponentPool,
               context: moderngl.Context):

        for entity_uid in list(component_pool.input_control_components.keys()):

            input_control = component_pool.input_control_components[entity_uid]
            if not input_control.active:
                continue

            transform = component_pool.transform_components[entity_uid]

            # TODO: Investigate why the directions seem to be reversed...

            # Rotate
            input_control.yaw += self.mouse_dx * input_control.mouse_sensitivity
            input_control.pitch -= self.mouse_dy * input_control.mouse_sensitivity
            input_control.pitch = np.clip(input_control.pitch, -np.pi * 0.49, np.pi * 0.49)

            # Translate
            if self.move_forward:
                transform.position += input_control.speed * input_control.forward
            if self.move_back:
                transform.position -= input_control.speed * input_control.forward
            if self.move_left:
                transform.position += input_control.speed * input_control.right
            if self.move_right:
                transform.position -= input_control.speed * input_control.right
            if self.move_up:
                transform.position -= input_control.speed * np.array((0, 1, 0), np.float32)
            if self.move_down:
                transform.position += input_control.speed * np.array((0, 1, 0), np.float32)

            # Update camera vectors
            """input_control.forward[0] = np.cos(input_control.yaw) * np.cos(input_control.pitch)
            input_control.forward[1] = np.sin(input_control.pitch)
            input_control.forward[2] = np.sin(input_control.yaw) * np.cos(input_control.pitch)

            input_control.forward = input_control.forward / np.linalg.norm(input_control.forward)
            right_temp = np.cross(input_control.forward, np.array((0, 1, 0)))
            input_control.right = right_temp / np.linalg.norm(right_temp)
            up_temp = np.cross(input_control.right, input_control.forward)
            input_control.up = up_temp / np.linalg.norm(up_temp)"""

    def on_event(self, event_type: int, event_data: tuple):

        # TODO: Add all indices to constants.py

        if event_type == constants.EVENT_MOUSE_SCROLL:
            pass

        if event_type == constants.EVENT_MOUSE_MOVE:
            if self.mouse_x_past is None:
                self.mouse_x_past = event_data[0]
            if self.mouse_y_past is None:
                self.mouse_y_past = event_data[1]

            self.mouse_dx = event_data[0] - self.mouse_x_past
            self.mouse_x_past = event_data[0]

            self.mouse_dy = event_data[1] - self.mouse_y_past
            self.mouse_y_past = event_data[1]

        if event_type == constants.EVENT_MOUSE_BUTTON_PRESS:
            pass

        if event_type == constants.EVENT_MOUSE_BUTTON_RELEASE:
            pass

        if event_type == constants.EVENT_KEYBOARD_PRESS:

            if event_data[0] == glfw.KEY_W:
                self.move_forward = True
                return

            if event_data[0] == glfw.KEY_S:
                self.move_back = True
                return

            if event_data[0] == glfw.KEY_A:
                self.move_left = True
                return

            if event_data[0] == glfw.KEY_D:
                self.move_right = True
                return

            if event_data[0] == glfw.KEY_E:
                self.move_up = True
                return

            if event_data[0] == glfw.KEY_Q:
                self.move_down = True
                return

        if event_type == constants.EVENT_KEYBOARD_RELEASE:

            if event_data[0] == glfw.KEY_W:
                self.move_forward = False
                return

            if event_data[0] == glfw.KEY_S:
                self.move_back = False
                return

            if event_data[0] == glfw.KEY_A:
                self.move_left = False
                return

            if event_data[0] == glfw.KEY_D:
                self.move_right = False
                return

            if event_data[0] == glfw.KEY_E:
                self.move_up = False
                return

            if event_data[0] == glfw.KEY_Q:
                self.move_down = False
                return

    def shutdown(self):
        pass