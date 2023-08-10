
# =============================================================================
#                               Event types
# =============================================================================

EVENT_KEYBOARD_PRESS = 1            # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_RELEASE = 2          # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_REPEAT = 3           # args: (key, scancode, mods) <int, int, int>

EVENT_MOUSE_BUTTON_PRESS = 4        # args: (button, mods) <int, int>
EVENT_MOUSE_BUTTON_RELEASE = 5      # args: (button, mods) <int, int>
EVENT_MOUSE_MOVE = 6                # args: (x, y) <float, float>
EVENT_MOUSE_SCROLL = 7              # args: (offset_x, offset_y) <float, float>

EVENT_WINDOW_RESIZE = 8                 # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_RESIZE = 9     # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 10             # args: (filepath, ...) <int, ...>  # TODO: Check if this should be a list


EVENT_LOAD_FILE = 1                 #args: (filepath) <str>

# =============================================================================
#                              GLFW Types
# =============================================================================

# Camera
CAMERA_Z_NEAR = 0.01
CAMERA_Z_FAR = 1000.0
CAMERA_ZOOM_SPEED = 0.05

# Mouse Input
MOUSE_LEFT = 0
MOUSE_RIGHT = 1
MOUSE_MIDDLE = 2
MOUSE_BUTTONS = (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)
MOUSE_POSITION = 'position'
MOUSE_POSITION_LAST_FRAME = 'position_last_frame'
MOUSE_SCROLL_POSITION = 'scroll_position'
MOUSE_SCROLL_POSITION_LAST_FRAME = 'scroll_position_last_frame'

BUTTON_PRESSED = 0
BUTTON_DOWN = 1
BUTTON_RELEASED = 2
BUTTON_UP = 3

# Keyboard
KEYBOARD_SIZE = 512  # Number of keys
KEY_STATE_DOWN = 0
KEY_STATE_UP = 1
KEY_LEFT_CTRL = 29
KEY_LEFT_SHIFT = 42
KEY_LEFT_ALT = 56