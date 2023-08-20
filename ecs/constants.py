import os

# Default Directories
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
SHADERS_DIRECTORY = os.path.join(RESOURCES_DIR, "shaders")

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

RENDER_SYSTEM_PROGRAM_FORWARD_PASS = "forward_pass"
RENDER_SYSTEM_PROGRAM_FRAGMENT_PICKING_PASS = "fragment_picking_pass"
RENDER_SYSTEM_PROGRAM_OUTLINE_PASS = "outline_pass"

# Input buffer names
SHADER_INPUT_VERTEX = "in_vert"
SHADER_INPUT_NORMAL = "in_normal"
SHADER_INPUT_COLOR = "in_color"
SHADER_INPUT_UV = "in_uv"

# Uniforms
SHADER_UNIFORM_ENTITY_ID = "entity_id"



# =============================================================================
#                              Component Pool
# =============================================================================

COMPONENT_TYPE_TRANSFORM_3D = 0
COMPONENT_TYPE_MESH = 1
COMPONENT_TYPE_CAMERA = 2
COMPONENT_TYPE_RENDERABLE = 3
COMPONENT_TYPE_MATERIAL = 4
COMPONENT_TYPE_INPUT_CONTROL = 5

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
SHADER_LIBRARY_FILE_EXTENSION = ".glsl"

SHADER_LIBRARY_DIRECTIVE_VERSION = "#version"
SHADER_LIBRARY_DIRECTIVE_DEFINE = "#define"
SHADER_LIBRARY_DIRECTIVE_INCLUDE = "#include"


SHADER_LIBRARY_AVAILABLE_TYPES = [
    SHADER_TYPE_VERTEX,
    SHADER_TYPE_GEOMETRY,
    SHADER_TYPE_FRAGMENT
]

