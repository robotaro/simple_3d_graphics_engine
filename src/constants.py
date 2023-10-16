import os
import numpy as np

# =============================================================================
#                                Directories
# =============================================================================

ECS_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(ECS_DIR)
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
SHADERS_DIRECTORY = os.path.join(ECS_DIR, "shaders")

# =============================================================================
#                                Editor
# =============================================================================

DEFAULT_EDITOR_WINDOW_SIZE = (1600, 900)  # (1280, 720)
DEFAULT_EDITOR_DOUBLE_CLICK_TIME_THRESHOLD = 0.5  # in seconds - Windows default is 500ms

SYSTEM_NAME_TRANSFORM = "transform_system"
SYSTEM_NAME_RENDER = "render_system"
SYSTEM_NAME_IMGUI = "imgui_system"
SYSTEM_NAME_INPUT_CONTROL = "input_control_system"
SYSTEM_NAME_GIZMO_3D = "gizmo_3d_system"
SYSTEM_NAME_IMPORT = "import_system"

AVAILABLE_SYSTEMS = [
    SYSTEM_NAME_TRANSFORM,
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI,
    SYSTEM_NAME_INPUT_CONTROL,
    SYSTEM_NAME_GIZMO_3D,
    SYSTEM_NAME_IMPORT
]

DEFAULT_SYSTEMS = [
    SYSTEM_NAME_IMPORT,
    SYSTEM_NAME_INPUT_CONTROL,
    SYSTEM_NAME_GIZMO_3D,
    SYSTEM_NAME_TRANSFORM,  # Must go BEFORE render system to read the transforms before they are shown!
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI  # Must come AFTER the render system to add the GUI to the final render
]

# =============================================================================
#                               Imgui System
# =============================================================================

IMGUI_DRAG_FLOAT_PRECISION = 1e-2

# =============================================================================
#                             Gizmo 3D System
# =============================================================================

GIZMO_3D_SYSTEM_X_AXIS_NAME = "x_axis"
GIZMO_3D_SYSTEM_Y_AXIS_NAME = "y_axis"
GIZMO_3D_SYSTEM_Z_AXIS_NAME = "z_axis"

# =============================================================================
#                               Events
# =============================================================================

# Types
EVENT_KEYBOARD_PRESS = 1            # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_RELEASE = 2          # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_REPEAT = 3           # args: (key, scancode, mods) <int, int, int>

EVENT_MOUSE_BUTTON_ENABLED = 10
EVENT_MOUSE_BUTTON_DISABLED = 11
EVENT_MOUSE_BUTTON_PRESS = 12        # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_BUTTON_RELEASE = 13      # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_MOVE = 14                # args: (x, y) <float, float>
EVENT_MOUSE_SCROLL = 15              # args: (offset_x, offset_y) <float, float>
EVENT_MOUSE_DOUBLE_CLICK = 16  # TODO: Implement this!!!

# Indices
EVENT_INDEX_KEYBOARD_KEY = 0
EVENT_INDEX_KEYBOARD_SCANCODE = 1
EVENT_INDEX_KEYBOARD_MODS = 2

EVENT_INDEX_MOUSE_BUTTON_BUTTON = 0
EVENT_INDEX_MOUSE_BUTTON_MODS = 1
EVENT_INDEX_MOUSE_BUTTON_X = 2
EVENT_INDEX_MOUSE_BUTTON_Y = 3
EVENT_INDEX_MOUSE_MOVE_X = 0
EVENT_INDEX_MOUSE_MOVE_Y = 1
EVENT_INDEX_MOUSE_SCROLL_X = 0
EVENT_INDEX_MOUSE_SCROLL_Y = 1

EVENT_EXIT_APPLICATION = 20
EVENT_ENTITY_SELECTED = 21
EVENT_ENTITY_DESELECTED = 22
EVENT_MULTIPLE_ENTITIES_SELECTED = 23

# Window
EVENT_WINDOW_SIZE = 30                # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_SIZE = 31    # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 32            # args: (filepath, ...) <int, ...>  # TODO: Check if this should be a

# =============================================================================
#                                Actions
# =============================================================================
ACTION_TRANSFORM_LOOK_AT = 0

# =============================================================================
#                              GLFW Types
# =============================================================================

# Camera
CAMERA_FOV_DEG = 45
CAMERA_Z_NEAR = 0.01
CAMERA_Z_FAR = 1000.0
CAMERA_VIEWPORT_RATIO = (0.0, 0.0, 1.0, 1.0)
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

RENDER_SYSTEM_UP_VECTOR = (0.0, 1.0, 0.0)
RENDER_SYSTEM_BACKGROUND_COLOR = (0.21176, 0.21176, 0.21176)

RENDER_SYSTEM_LAYER_DEFAULT = 0
RENDER_SYSTEM_LAYER_DEBUG = 1
RENDER_SYSTEM_LAYER_GIZMO_3D = 2
RENDER_SYSTEM_LAYER_SKELETON = 5
RENDER_SYSTERM_LAYERS = [
    RENDER_SYSTEM_LAYER_DEFAULT,
    RENDER_SYSTEM_LAYER_DEBUG,
    RENDER_SYSTEM_LAYER_GIZMO_3D
]

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

RENDER_MODE_COLOR_SOURCE_SINGLE = 0
RENDER_MODE_COLOR_SOURCE_BUFFER = 1
RENDER_MODE_COLOR_SOURCE_UV = 2
COLOR_SOURCE_MAP = {
    "single": RENDER_MODE_COLOR_SOURCE_SINGLE,
    "buffer": RENDER_MODE_COLOR_SOURCE_BUFFER,
    "uv": RENDER_MODE_COLOR_SOURCE_UV
}

RENDER_MODE_LIGHTING_SOLID = 0
RENDER_MODE_LIGHTING_LIT = 1
LIGHTING_MODE_MAP = {
    "solid": RENDER_MODE_LIGHTING_SOLID,
    "lit": RENDER_MODE_LIGHTING_LIT
}

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

DIRECTIONAL_LIGHT_TEXTURE_SIZE = (2048, 2048)

# =============================================================================
#                              Transform System
# =============================================================================

TRANSFORM_SYSTEM_MAX_NUM_TRANSFORMS = 256

# =============================================================================
#                                  Math
# =============================================================================

DEG2RAD = 3.14159265358979 / 180.0

# =============================================================================
#                              Component Pool
# =============================================================================

COMPONENT_POOL_STARTING_ID_COUNTER = 2

# Component Types
COMPONENT_TYPE_TRANSFORM_3D = 0
COMPONENT_TYPE_TRANSFORM_2D = 1
COMPONENT_TYPE_MESH = 2
COMPONENT_TYPE_CAMERA = 3
COMPONENT_TYPE_MATERIAL = 4
COMPONENT_TYPE_INPUT_CONTROL = 5
COMPONENT_TYPE_TEXT_2D = 6
COMPONENT_TYPE_DIRECTIONAL_LIGHT = 7
COMPONENT_TYPE_SPOT_LIGHT = 8
COMPONENT_TYPE_POINT_LIGHT = 9
COMPONENT_TYPE_COLLIDER = 10
COMPONENT_TYPE_GIZMO_3D = 11

# Component Names (For loading from XML)
COMPONENT_NAME_TRANSFORM_3D = "transform_3d"
COMPONENT_NAME_MESH = "mesh"
COMPONENT_NAME_CAMERA = "camera"
COMPONENT_NAME_MATERIAL = "material"
COMPONENT_NAME_INPUT_CONTROL = "input_control"
COMPONENT_NAME_TEXT_2D = "text_2d"
COMPONENT_NAME_DIRECTIONAL_LIGHT = "directional_light"
COMPONENT_NAME_SPOT_LIGHT = "spot_light"
COMPONENT_NAME_POINT_LIGHT = "point_light"
COMPONENT_NAME_COLLIDER = "collider"
COMPONENT_NAME_GIZMO_3D = "gizmo_3d"

COMPONENT_MAP = {
    COMPONENT_NAME_TRANSFORM_3D: COMPONENT_TYPE_TRANSFORM_3D,
    COMPONENT_NAME_MESH: COMPONENT_TYPE_MESH,
    COMPONENT_NAME_CAMERA: COMPONENT_TYPE_CAMERA,
    COMPONENT_NAME_MATERIAL: COMPONENT_TYPE_MATERIAL,
    COMPONENT_NAME_INPUT_CONTROL: COMPONENT_TYPE_INPUT_CONTROL,
    COMPONENT_NAME_TEXT_2D: COMPONENT_TYPE_TEXT_2D,
    COMPONENT_NAME_DIRECTIONAL_LIGHT: COMPONENT_TYPE_DIRECTIONAL_LIGHT,
    COMPONENT_NAME_SPOT_LIGHT: COMPONENT_TYPE_SPOT_LIGHT,
    COMPONENT_NAME_POINT_LIGHT: COMPONENT_TYPE_POINT_LIGHT,
    COMPONENT_NAME_COLLIDER: COMPONENT_TYPE_COLLIDER,
    COMPONENT_NAME_GIZMO_3D: COMPONENT_TYPE_GIZMO_3D
}

# Mesh Component Arguments
COMPONENT_ARG_MESH_SHAPE = "shape"
COMPONENT_ARG_MESH_FPATH = "fpath"

MESH_SHAPE_BOX = "box"
MESH_SHAPE_ICOSPHERE = "icosphere"
MESH_SHAPE_CAPSULE = "capsule"
MESH_SHAPE_CYLINDER = "cylinder"
MESH_SHAPE_FROM_OBJ = "obj"  # TODO: Kinda of a hack. You need to add argument "fpath"
MESH_SHAPE_FROM_GLTF = "dae"

COLLIDER_SHAPE_SPHERE = "sphere"
COLLIDER_SHAPE_CAPSULE = "capsule"
COLLIDER_SHAPE_PLANE = "plane"

# =============================================================================
#                               Materials
# =============================================================================

MATERIAL_COLOR_BLACK = (0.0, 0.0, 0.0)
MATERIAL_COLOR_WHITE = (1.0, 1.0, 1.0)
MATERIAL_COLOR_RED = (1.0, 0.0, 0.0)
MATERIAL_COLOR_LIME = (0.0, 1.0, 0.0)
MATERIAL_COLOR_BLUE = (0.0, 0.0, 1.0)
MATERIAL_COLOR_YELLOW = (1.0, 1.0, 0.0)
MATERIAL_COLOR_CYAN = (0.0, 1.0, 1.0)  # Also known as Aqua
MATERIAL_COLOR_MAGENTA = (1.0, 0.0, 1.0)  # Also known as Fuchsia
MATERIAL_COLOR_SILVER = (192.0 / 255.0, 192.0 / 255.0, 192.0 / 255.0)
MATERIAL_COLOR_GRAY = (128.0 / 255.0, 128.0 / 255.0, 128.0 / 255.0)
MATERIAL_COLOR_MAROON = (128.0 / 255.0, 0.0, 0.0)
MATERIAL_COLOR_OLIVE = (128.0 / 255.0, 128.0 / 255.0, 0.0)
MATERIAL_COLOR_GREEN = (0.0, 128.0 / 255.0, 0.0)
MATERIAL_COLOR_PURPLE = (128.0 / 255.0, 0.0, 128.0 / 255.0)
MATERIAL_COLOR_TEAL = (0.0, 128.0 / 255.0, 128.0 / 255.0)
MATERIAL_COLOR_NAVY = (0.0, 0.0, 128.0 / 255.0)


# From: https://stackoverflow.com/questions/64369710/what-are-the-hex-codes-of-matplotlib-tab10-palette
MATERIAL_COLOR_TAB10_BLUE = (31 / 255.0, 119 / 255.0, 180 / 255.0)  # #1f77b4
MATERIAL_COLOR_TAB10_ORANGE = (255 / 255.0, 127 / 255.0, 14 / 255.0)  # #ff7f0e
MATERIAL_COLOR_TAB10_GREEN = (44 / 255.0, 160 / 255.0, 44 / 255.0)  # #2ca02c
MATERIAL_COLOR_TAB10_RED = (214 / 255.0, 39 / 255.0, 40 / 255.0)  #d62728
MATERIAL_COLOR_TAB10_PURPLE = (148 / 255.0, 103 / 255.0, 189 / 255.0)  # #9467bd
MATERIAL_COLOR_TAB10_BROWN = (140 / 255.0, 86 / 255.0, 75 / 255.0)  # #8c564b
MATERIAL_COLOR_TAB10_PINK = (227 / 255.0, 119 / 255.0, 194 / 255.0)  # #e377c2
MATERIAL_COLOR_TAB10_GRAY = (127 / 255.0, 127 / 255.0, 127 / 255.0)  # #7f7f7f
MATERIAL_COLOR_TAB10_OLIVE = (188 / 255.0, 189 / 255.0, 34 / 255.0)  # #bcbd22
MATERIAL_COLOR_TAB10_CYAN = (23 / 255.0, 190 / 255.0, 207 / 255.0)  #17becf

MATERIAL_COLORS = {
    "black": MATERIAL_COLOR_BLACK,
    "white": MATERIAL_COLOR_WHITE,
    "red": MATERIAL_COLOR_RED,
    "lime": MATERIAL_COLOR_LIME,
    "blue": MATERIAL_COLOR_BLUE,
    "yellow": MATERIAL_COLOR_YELLOW,
    "cyan": MATERIAL_COLOR_CYAN,  # Also known as Aqua
    "aqua": MATERIAL_COLOR_CYAN,  # Also known as Cyan
    "magenta": MATERIAL_COLOR_MAGENTA,  # Also known as Fuchsia
    "fuchsia": MATERIAL_COLOR_MAGENTA,  # Also known as Magenta
    "silver": MATERIAL_COLOR_SILVER,
    "gray": MATERIAL_COLOR_GRAY,
    "maroon": MATERIAL_COLOR_MAROON,
    "olive": MATERIAL_COLOR_OLIVE,
    "green": MATERIAL_COLOR_GREEN,
    "purple": MATERIAL_COLOR_PURPLE,
    "teal": MATERIAL_COLOR_TEAL,
    "navy": MATERIAL_COLOR_NAVY,
    "tab10_blue": MATERIAL_COLOR_TAB10_BLUE,
    "tab10_orange": MATERIAL_COLOR_TAB10_ORANGE,
    "tab10_green": MATERIAL_COLOR_TAB10_GREEN,
    "tab10_red": MATERIAL_COLOR_TAB10_RED,
    "tab10_purple": MATERIAL_COLOR_TAB10_PURPLE,
    "tab10_brown": MATERIAL_COLOR_TAB10_BROWN,
    "tab10_pink": MATERIAL_COLOR_TAB10_PINK,
    "tab10_gray": MATERIAL_COLOR_TAB10_GRAY,
    "tab10_olive": MATERIAL_COLOR_TAB10_OLIVE,
    "tab10_cyan": MATERIAL_COLOR_TAB10_CYAN
}

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
SHADER_LIBRARY_YAML_KEY_INPUT_TEXTURE_LOCATION = "input_texture_location"
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
