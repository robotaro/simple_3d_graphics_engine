import os

# Default Directories
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
SHADERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaders")

# Default OpenGL constants
OPENGL_MAJOR_VERSION = 4
OPENGL_MINOR_VERSION = 0

# Window
WINDOW_DEFAULT_SIZE = (1280, 720)
WINDOW_DEFAULT_TITLE = "Application Window"

# OpenGL Shaders
MACRO_DEFINED_VERTEX_SHADER = "#define VERTEX_SHADER"
MACRO_DEFINED_GEOMETRY_SHADER = "#define GEOMETRY_SHADER"
MACRO_DEFINED_FRAGMENT_SHADER = "#define FRAGMENT_SHADER"

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


BACKGROUND_COLOR_RGB = (0.08, 0.16, 0.18)

# Font
FONT_VERTICES_NUM_COLUMNS = 12  # 6 vertices, 2 dimensions each
FONT_UVS_NUM_COLUMNS = 12  # 6 vertices, 2 dimensions each


