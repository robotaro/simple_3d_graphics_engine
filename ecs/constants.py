import os

# =============================================================================
#                                Directories
# =============================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
SHADERS_DIRECTORY = os.path.join(RESOURCES_DIR, "shaders")

# =============================================================================
#                               Editor
# =============================================================================

SYSTEM_NAME_RENDER = "render_system"
SYSTEM_NAME_IMGUI = "imgui_system"
SYSTEM_NAME_INPUT_CONTROL = "input_control_system"
AVAILABLE_SYSTEMS = [
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI
]
# =============================================================================
#                               Event types
# =============================================================================

# Keyboard
EVENT_KEYBOARD_PRESS = 1            # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_RELEASE = 2          # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_REPEAT = 3           # args: (key, scancode, mods) <int, int, int>
EVENT_INDEX_KEYBOARD_KEY = 0
EVENT_INDEX_KEYBOARD_SCANCODE = 1
EVENT_INDEX_KEYBOARD_MODS = 2

# Mouse
EVENT_MOUSE_BUTTON_PRESS = 4        # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_BUTTON_RELEASE = 5      # args: (button, mods, x, y) <int, int, int, int>
EVENT_INDEX_MOUSE_BUTTON_BUTTON = 0
EVENT_INDEX_MOUSE_BUTTON_MODS = 1
EVENT_INDEX_MOUSE_BUTTON_X = 2
EVENT_INDEX_MOUSE_BUTTON_Y = 3

EVENT_MOUSE_MOVE = 6                # args: (x, y) <float, float>
EVENT_INDEX_MOUSE_MOVE_X = 0
EVENT_INDEX_MOUSE_MOVE_Y = 1

EVENT_MOUSE_SCROLL = 7              # args: (offset_x, offset_y) <float, float>
EVENT_INDEX_MOUSE_SCROLL_X = 0
EVENT_INDEX_MOUSE_SCROLL_Y = 1

# Window
EVENT_WINDOW_RESIZE = 8                 # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_RESIZE = 9     # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 10            # args: (filepath, ...) <int, ...>  # TODO: Check if this should be a list

EVENT_LOAD_FILE = 1                 #args: (filepath) <str>

# =============================================================================
#                              GLFW Types
# =============================================================================

# Camera
CAMERA_FOV_DEG = 45
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
KEYBOARD_SIZE = 512
KEY_STATE_DOWN = 0
KEY_STATE_UP = 1
KEY_LEFT_CTRL = 29
KEY_LEFT_SHIFT = 42
KEY_LEFT_ALT = 56

# Viewport
VIEWPORT_INDEX_X = 0
VIEWPORT_INDEX_Y = 1
VIEWPORT_INDEX_WIDTH = 2
VIEWPORT_INDEX_HEIGHT = 3

# =============================================================================
#                                Render System
# =============================================================================

RENDER_3D_SYSTEM_MODE_FINAL = 0
RENDER_3D_SYSTEM_MODE_NORMAL = 1
RENDER_3D_SYSTEM_MODE_DEPTH = 2
RENDER_3D_SYSTEM_MODE_ENTITY_ID = 3
RENDER_3D_SYSTEM_MODE_INSTANCE_ID = 4

SHADER_PROGRAM_FORWARD_PASS = "forward_pass"
SHADER_PROGRAM_SELECTED_ENTITY_PASS = "selected_entity_pass"
SHADER_PROGRAM_OUTLINE_PASS = "outline_pass"
SHADER_PROGRAM_TEXT_2D = "text_2d"
SHADER_PASSES_LIST = [
    SHADER_PROGRAM_FORWARD_PASS,
    SHADER_PROGRAM_SELECTED_ENTITY_PASS
]

# Input buffer names
SHADER_INPUT_VERTEX = "in_vert"
SHADER_INPUT_NORMAL = "in_normal"
SHADER_INPUT_COLOR = "in_color"
SHADER_INPUT_UV = "in_uv"

# Uniforms
SHADER_UNIFORM_ENTITY_ID = "entity_id"

# Font
FONT_NUM_VERTICES_PER_CHAR = 12
FONT_CHAR_SIZE = 32  # Resolution dpi, not actual pixels
FONT_SHEET_ROWS = 16
FONT_SHEET_COLS = 16
FONT_SHEET_CELL_WIDTH = 32
FONT_SHEET_CELL_HEIGHT = 32
FONT_NUM_GLYPHS = FONT_SHEET_ROWS * FONT_SHEET_COLS
FONT_TEXTURE_WIDTH = FONT_SHEET_CELL_WIDTH * FONT_SHEET_COLS
FONT_TEXTURE_HEIGHT = FONT_SHEET_CELL_HEIGHT * FONT_SHEET_ROWS



# =============================================================================
#                              Component Pool
# =============================================================================

COMPONENT_TYPE_TRANSFORM_3D = 0
COMPONENT_TYPE_MESH = 1
COMPONENT_TYPE_CAMERA = 2
COMPONENT_TYPE_RENDERABLE = 3
COMPONENT_TYPE_MATERIAL = 4
COMPONENT_TYPE_INPUT_CONTROL = 5
COMPONENT_TYPE_TEXT_2D = 6

# Mesh Component Arguments
COMPONENT_ARG_MESH_SHAPE = "shape"
COMPONENT_ARG_MESH_FPATH = "fpath"

MESH_SHAPE_CUBE = "cube"
MESH_SHAPE_SPHERE = "sphere"
MESH_SHAPE_CYLINDER = "cylinder"
MESH_SHAPE_FROM_OBJ = "obj"  # TODO: Kinda of a hack. You need to add argument "fpath"

# =============================================================================
#                              Shader Library
# =============================================================================
SHADER_TYPE_VERTEX = "vertex"
SHADER_TYPE_GEOMETRY = "geometry"
SHADER_TYPE_FRAGMENT = "fragment"

SHADER_LIBRARY_YAML_KEY_DEFINE = "define"  # For extra definitions
SHADER_LIBRARY_YAML_KEY_VARYING = "varying"  # For varying variables (those who output to VBos rather than textures)
SHADER_LIBRARY_FILE_EXTENSION = ".glsl"

SHADER_LIBRARY_DIRECTIVE_VERSION = "#version"
SHADER_LIBRARY_DIRECTIVE_DEFINE = "#define"
SHADER_LIBRARY_DIRECTIVE_INCLUDE = "#include"

SHADER_LIBRARY_AVAILABLE_TYPES = [
    SHADER_TYPE_VERTEX,
    SHADER_TYPE_GEOMETRY,
    SHADER_TYPE_FRAGMENT
]