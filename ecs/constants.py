import os
import numpy as np

# =============================================================================
#                                Directories
# =============================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
SHADERS_DIRECTORY = os.path.join(RESOURCES_DIR, "shaders")

# =============================================================================
#                                Editor
# =============================================================================

DEFAULT_EDITOR_WINDOW_SIZE = (1600, 900)
SYSTEM_NAME_RENDER = "render_system"
SYSTEM_NAME_IMGUI = "imgui_system"
SYSTEM_NAME_INPUT_CONTROL = "input_control_system"
AVAILABLE_SYSTEMS = [
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI
]

# =============================================================================
#                               Imgui System
# =============================================================================

IMGUI_DRAG_FLOAT_PRECISION = 1e-2

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
EVENT_MOUSE_BUTTON_ENABLED = 10
EVENT_MOUSE_BUTTON_DISABLED = 11
EVENT_MOUSE_BUTTON_PRESS = 12        # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_BUTTON_RELEASE = 13      # args: (button, mods, x, y) <int, int, int, int>

EVENT_INDEX_MOUSE_BUTTON_BUTTON = 0
EVENT_INDEX_MOUSE_BUTTON_MODS = 1
EVENT_INDEX_MOUSE_BUTTON_X = 2
EVENT_INDEX_MOUSE_BUTTON_Y = 3

EVENT_MOUSE_MOVE = 14                # args: (x, y) <float, float>
EVENT_INDEX_MOUSE_MOVE_X = 0
EVENT_INDEX_MOUSE_MOVE_Y = 1

EVENT_MOUSE_SCROLL = 15              # args: (offset_x, offset_y) <float, float>
EVENT_INDEX_MOUSE_SCROLL_X = 0
EVENT_INDEX_MOUSE_SCROLL_Y = 1

# Actions
EVENT_ACTION_ENTITY_SELECTED = 20

# Window
EVENT_WINDOW_RESIZE = 30                # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_RESIZE = 31    # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 32            # args: (filepath, ...) <int, ...>  # TODO: Check if this should be a list


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

RENDER_SYSTEM_DEFAULT_UP_VECTOR = (0.0, 1.0, 0.0)

RENDER_3D_SYSTEM_MODE_FINAL = 0
RENDER_3D_SYSTEM_MODE_NORMAL = 1
RENDER_3D_SYSTEM_MODE_DEPTH = 2
RENDER_3D_SYSTEM_MODE_ENTITY_ID = 3
RENDER_3D_SYSTEM_MODE_INSTANCE_ID = 4

SHADER_PROGRAM_FORWARD_PASS = "forward_pass"
SHADER_PROGRAM_SELECTED_ENTITY_PASS = "selected_entity_pass"
SHADER_PROGRAM_SHADOW_MAPPING_PASS = "shadow_mapping"
SHADER_PROGRAM_TEXT_2D = "text_2d"
SHADER_PASSES_LIST = [
    SHADER_PROGRAM_FORWARD_PASS,
    SHADER_PROGRAM_SELECTED_ENTITY_PASS,
    SHADER_PROGRAM_SHADOW_MAPPING_PASS
]

# Input buffer names
SHADER_INPUT_VERTEX = "in_vert"
SHADER_INPUT_NORMAL = "in_normal"
SHADER_INPUT_COLOR = "in_color"
SHADER_INPUT_UV = "in_uv"

# Uniforms
SHADER_UNIFORM_ENTITY_ID = "entity_id"

# Font Library
FONT_VBO_BUFFER_RESERVE = 4096
FONT_NUM_VERTICES_PER_CHAR = 12
FONT_CHAR_SIZE = 48  # Resolution dpi, not actual pixels
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

COMPONENT_POOL_STARTING_ID_COUNTER = 2

# Component Types
COMPONENT_TYPE_TRANSFORM_3D = 0
COMPONENT_TYPE_TRANSFORM_2D = 1
COMPONENT_TYPE_MESH = 2
COMPONENT_TYPE_CAMERA = 3
COMPONENT_TYPE_RENDERABLE = 4
COMPONENT_TYPE_MATERIAL = 5
COMPONENT_TYPE_INPUT_CONTROL = 6
COMPONENT_TYPE_TEXT_2D = 7
COMPONENT_TYPE_DIRECTIONAL_LIGHT = 8
COMPONENT_TYPE_SPOT_LIGHT = 9
COMPONENT_TYPE_POINT_LIGHT = 10

# Component Names (For loading from XML)
COMPONENT_NAME_TRANSFORM_3D = "transform_3d"
COMPONENT_NAME_TRANSFORM_2D = "transform_2d"
COMPONENT_NAME_MESH = "mesh"
COMPONENT_NAME_CAMERA = "camera"
COMPONENT_NAME_RENDERABLE = "renderable"
COMPONENT_NAME_MATERIAL = "material"
COMPONENT_NAME_INPUT_CONTROL = "input_control"
COMPONENT_NAME_TEXT_2D = "text_2d"
COMPONENT_NAME_DIRECTIONAL_LIGHT = "directional_light"
COMPONENT_NAME_SPOT_LIGHT = "spot_light"
COMPONENT_NAME_POINT_LIGHT = "point_light"

# Mesh Component Arguments
COMPONENT_ARG_MESH_SHAPE = "shape"
COMPONENT_ARG_MESH_FPATH = "fpath"

MESH_SHAPE_BOX = "box"
MESH_SHAPE_SPHERE = "sphere"
MESH_SHAPE_CYLINDER = "cylinder"
MESH_SHAPE_FROM_OBJ = "obj"  # TODO: Kinda of a hack. You need to add argument "fpath"

# =============================================================================
#                               Transforms
# =============================================================================

TRANSFORMS_UP_VECTOR = np.array((0, 1, 0), dtype=np.float32)

# =============================================================================
#                              Shader Library
# =============================================================================
SHADER_TYPE_VERTEX = "vertex"
SHADER_TYPE_GEOMETRY = "geometry"
SHADER_TYPE_FRAGMENT = "fragment"

SHADER_LIBRARY_YAML_KEY_DEFINE = "define"  # For extra definitions
SHADER_LIBRARY_YAML_KEY_VARYING = "varying"  # For varying variables (those who output to VBos rather than textures)
SHADER_LIBRARY_YAML_KEY_SAMPLER_2D_LOCATION = "sampler_2d_location"
SHADER_LIBRARY_FILE_EXTENSION = ".glsl"

SHADER_LIBRARY_DIRECTIVE_VERSION = "#version"
SHADER_LIBRARY_DIRECTIVE_DEFINE = "#define"
SHADER_LIBRARY_DIRECTIVE_INCLUDE = "#include"

SHADER_LIBRARY_AVAILABLE_TYPES = [
    SHADER_TYPE_VERTEX,
    SHADER_TYPE_GEOMETRY,
    SHADER_TYPE_FRAGMENT
]

# =============================================================================
#                                Font Library
# =============================================================================

FONT_LIBRARY_NUM_CHARACTERS = 256
FONT_LIBRARY_NUM_PARAMETERS = 10

FONT_LIBRARY_COLUMN_INDEX_X = 0
FONT_LIBRARY_COLUMN_INDEX_Y = 1
FONT_LIBRARY_COLUMN_INDEX_WIDTH = 2
FONT_LIBRARY_COLUMN_INDEX_HEIGHT = 3
FONT_LIBRARY_COLUMN_INDEX_U_MIN = 4
FONT_LIBRARY_COLUMN_INDEX_V_MIN = 5
FONT_LIBRARY_COLUMN_INDEX_U_MAX = 6
FONT_LIBRARY_COLUMN_INDEX_V_MAX = 7
FONT_LIBRARY_COLUMN_INDEX_VERTICAL_OFFSET = 8
FONT_LIBRARY_COLUMN_INDEX_HORIZONTAL_ADVANCE = 9
