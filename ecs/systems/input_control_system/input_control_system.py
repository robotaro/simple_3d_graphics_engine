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
        self.mouse_dx = None
        self.mouse_dy = None

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

            #input_control.update_camera_vectors()


    def on_event(self, event_type: int, event_data: tuple):

        self.latest_event = event_type
        self.latest_event_data = event_data

        # TODO: Add all indices to constants.py

        if event_type == constants.EVENT_MOUSE_SCROLL:
            pass

        if event_type == constants.EVENT_MOUSE_MOVE:
            pass

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
