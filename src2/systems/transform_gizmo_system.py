from src2.systems.system import System
from src2.core import constants


class SystemTransformGizmo(System):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_subscribed_events(self):
        return [
            constants.EVENT_KEYBOARD_PRESS
        ]

    def handle_event_keyboard_press(self, key, scancode, mods):
        pass