import os
import numpy as np

# =============================================================================
#                                Directories
# =============================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
SHADERS_DIR = os.path.join(SRC_DIR, "shaders")

# =============================================================================
#                                Editor
# =============================================================================

DEFAULT_EDITOR_PROFILING_UPDATE_PERIOD = 0.5  # Seconds
DEFAULT_EDITOR_WINDOW_SIZE = (1600, 900)  # (1280, 720)
DEFAULT_EDITOR_DOUBLE_CLICK_TIME_THRESHOLD = 0.5  # in seconds - Windows default is 500ms

MODULE_NAME_DATA_MANAGER = "data_manager"

SYSTEM_NAME_TRANSFORM = "transform_system"
SYSTEM_NAME_RENDER = "render_system"
SYSTEM_NAME_IMGUI = "imgui_system"
SYSTEM_NAME_INPUT_CONTROL = "input_control_system"
SYSTEM_NAME_GIZMO_3D = "gizmo_3d_system"
SYSTEM_NAME_IMPORT = "import_system"
SYSTEM_NAME_SKELETON = "skeleton_system"

AVAILABLE_SYSTEMS = [
    SYSTEM_NAME_TRANSFORM,
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI,
    SYSTEM_NAME_INPUT_CONTROL,
    SYSTEM_NAME_GIZMO_3D,
    SYSTEM_NAME_IMPORT
]

DEFAULT_SYSTEMS = [
    SYSTEM_NAME_INPUT_CONTROL,
    SYSTEM_NAME_GIZMO_3D,
    SYSTEM_NAME_TRANSFORM,  # Must go BEFORE render system to read the transforms before they are shown!
    SYSTEM_NAME_SKELETON,
    SYSTEM_NAME_RENDER,
    SYSTEM_NAME_IMGUI  # Must come AFTER the render system to add the GUI to the final render
]

# =============================================================================
#                                 Resources
# =============================================================================

RESOURCE_TYPE_MESH = "mesh"
RESOURCE_TYPE_SKELETON = "skeleton"
RESOURCE_TYPE_ANIMATION = "animation"
RESOURCE_TYPE_NODES_GLTF = "nodes"
RESOURCE_TYPE_ANIMATION_BVH = "animation_bvh"

RESOURCE_ANIMATION_GLTF_CHANNELS = ["translation", "rotation", "scale"]

RESOURCE_BVH_ROTATION_ORDER_MAP = {
    "xyz": 0,
    "xzy": 1,
    "yxz": 2,
    "yzx": 3,
    "zxy": 4,
    "zyx": 5
}


# =============================================================================
#                               Imgui System
# =============================================================================

IMGUI_DRAG_FLOAT_PRECISION = 1e-2

# =============================================================================
#                             Gizmo 3D System
# =============================================================================

# Orientations
GIZMO_3D_ORIENTATION_GLOBAL = 0
GIZMO_3D_ORIENTATION_LOCAL = 1

# Planes
GIZMO_3D_PLANE_XY = 0
GIZMO_3D_PLANE_YZ = 1
GIZMO_3D_PLANE_XZ = 2
GIZMO_3D_PLANE_CAMERA = 3

# Modes
GIZMO_3D_MODE_TRANSLATION = 0
GIZMO_3D_MODE_ROTATION = 2
GIZMO_3D_MODE_SCALE = 1

# Internal States
GIZMO_3D_STATE_NOT_HOVERING = 0
GIZMO_3D_STATE_HOVERING_AXIS = 1
GIZMO_3D_STATE_HOVERING_PLANE = 2
GIZMO_3D_STATE_TRANSLATING_ON_AXIS = 3
GIZMO_3D_STATE_TRANSLATING_ON_PLANE = 4
GIZMO_3D_STATE_ROTATE_AROUND_AXIS = 5

GIZMO_3D_SYSTEM_X_AXIS_NAME = "x_axis"
GIZMO_3D_SYSTEM_Y_AXIS_NAME = "y_axis"
GIZMO_3D_SYSTEM_Z_AXIS_NAME = "z_axis"
GIZMO_3D_AXES_NAME_ORDER = [
    GIZMO_3D_SYSTEM_X_AXIS_NAME,
    GIZMO_3D_SYSTEM_Y_AXIS_NAME,
    GIZMO_3D_SYSTEM_Z_AXIS_NAME
]
GIZMO_3D_SCALE_COEFFICIENT = 0.1
GIZMO_3D_AXES = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
GIZMO_3D_ANGLE_TANGENT_COEFFICIENT = np.tan(5.0 * np.pi / 180.0)
GIZMO_3D_VIEWPORT_SCALE_COEFFICIENT = 1000.0

# =============================================================================
#                               Events
# =============================================================================

# Basic types
EVENT_KEYBOARD_PRESS = 1            # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_RELEASE = 2          # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_REPEAT = 3           # args: (key, scancode, mods) <int, int, int>
EVENT_MOUSE_ENTER_UI = 10
EVENT_MOUSE_LEAVE_UI = 11
EVENT_MOUSE_BUTTON_PRESS = 12        # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_BUTTON_RELEASE = 13      # args: (button, mods, x, y) <int, int, int, int>
EVENT_MOUSE_MOVE = 14                # args: (x, y_gl, y_gui) <float, float>
EVENT_MOUSE_SCROLL = 15              # args: (offset_x, offset_y) <float, float>
EVENT_MOUSE_DOUBLE_CLICK = 16
EVENT_MOUSE_ENTER_GIZMO_3D = 17
EVENT_MOUSE_LEAVE_GIZMO_3D = 18
EVENT_MOUSE_GIZMO_3D_ACTIVATED = 19
EVENT_MOUSE_GIZMO_3D_DEACTIVATED = 20
EVENT_EXIT_APPLICATION = 20
EVENT_ENTITY_SELECTED = 21
EVENT_ENTITY_DESELECTED = 22
EVENT_MULTIPLE_ENTITIES_SELECTED = 23
EVENT_PROFILING_SYSTEM_PERIODS = 24  # args (("system_a", 0.2), ("system_b" 0.37), ...) <(string, float) ...>

# System inter-communication
EVENT_GIZMO_3D_SYSTEM_PARAMETER_UPDATED = 100
EVENT_RENDER_SYSTEM_PARAMETER_UPDATED = 101

# Indices
EVENT_INDEX_KEYBOARD_KEY = 0
EVENT_INDEX_KEYBOARD_SCANCODE = 1
EVENT_INDEX_KEYBOARD_MODS = 2

EVENT_INDEX_MOUSE_BUTTON_BUTTON = 0
EVENT_INDEX_MOUSE_BUTTON_MODS = 1
EVENT_INDEX_MOUSE_BUTTON_X = 2
EVENT_INDEX_MOUSE_BUTTON_Y_OPENGL = 3
EVENT_INDEX_MOUSE_BUTTON_Y_GUI = 4
EVENT_INDEX_MOUSE_MOVE_X = 0
EVENT_INDEX_MOUSE_MOVE_Y_OPENGL = 1
EVENT_INDEX_MOUSE_MOVE_Y_GUI = 2
EVENT_INDEX_MOUSE_SCROLL_X = 0
EVENT_INDEX_MOUSE_SCROLL_Y = 1


# Window
EVENT_WINDOW_SIZE = 30                # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_SIZE = 31    # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 32          # args: (filepath, ...) <str, ...>


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
#                                     Scene
# =============================================================================

# UBO definitions
UBO_BINDING_CAMERA_SETTINGS = 0
UBO_BINDING_MATERIALS = 1
UBO_BINDING_POINT_LIGHTS = 2
UBO_BINDING_DIRECTIONAL_LIGHTS = 3
UBO_BINDING_TRANSFORMS = 4

SCENE_MAX_NUM_MATERIALS = 32
SCENE_MAX_NUM_POINT_LIGHTS = 8
SCENE_MAX_NUM_DIRECTIONAL_LIGHTS = 4
SCENE_MAX_NUM_TRANSFORMS = 128

SCENE_CAMERA_SETTINGS_STRUCT_SIZE_BYTES = 256
SCENE_MATERIAL_STRUCT_SIZE_BYTES = 64
SCENE_POINT_LIGHT_STRUCT_SIZE_BYTES = 64
SCENE_POINT_TRANSFORM_SIZE_BYTES = 64

# =============================================================================
#                                Render System
# =============================================================================

RENDER_SYSTEM_UP_VECTOR = (0.0, 1.0, 0.0)
RENDER_SYSTEM_BACKGROUND_COLOR = (0.21176, 0.21176, 0.21176)

RENDER_SYSTEM_LAYER_DEFAULT = 0
RENDER_SYSTEM_LAYER_OVERLAY = 1

SHADER_PROGRAM_FORWARD_PASS = "forward_pass"
SHADER_PROGRAM_DEBUG_FORWARD_PASS = "debug_forward_pass"
SHADER_PROGRAM_OVERLAY_3D_PASS = "overlay_3d_pass"
SHADER_PROGRAM_OVERLAY_2D_PASS = "overlay_2d_pass"
SHADER_PROGRAM_SELECTED_ENTITY_PASS = "selected_entity_pass"
SHADER_PROGRAM_SHADOW_MAPPING_PASS = "shadow_mapping"
SHADER_PASSES_LIST = [
    SHADER_PROGRAM_FORWARD_PASS,
    SHADER_PROGRAM_OVERLAY_3D_PASS,
    SHADER_PROGRAM_OVERLAY_2D_PASS,
    SHADER_PROGRAM_SELECTED_ENTITY_PASS,
    SHADER_PROGRAM_SHADOW_MAPPING_PASS
]

# =============[ Render Commands ]===============

MAX_RENDER_COMMANDS = 4096

# Bit allocation
LAYER_BITS = 8
TRANSPARENCY_BITS = 1
DISTANCE_BITS = 16
MATERIAL_BITS = 8
MESH_BITS = 12
TRANSFORM_BITS = 12
RENDER_MODE_BITS = 4

TOTAL_USED_BITS = LAYER_BITS + TRANSPARENCY_BITS + DISTANCE_BITS + MATERIAL_BITS + MESH_BITS + TRANSFORM_BITS + RENDER_MODE_BITS
if TOTAL_USED_BITS > 64:
    raise Exception(f"[ERROR] Total number bits in render command is {TOTAL_USED_BITS} ")

# Shifts
RENDER_MODE_SHIFT = 0
TRANSFORM_SHIFT = RENDER_MODE_SHIFT + RENDER_MODE_BITS
MESH_SHIFT = TRANSFORM_SHIFT + TRANSFORM_BITS
MATERIAL_SHIFT = MESH_SHIFT + MESH_BITS
DISTANCE_SHIFT = MATERIAL_SHIFT + MATERIAL_BITS
TRANSPARENCY_SHIFT = DISTANCE_SHIFT + DISTANCE_BITS
LAYER_SHIFT = TRANSPARENCY_SHIFT + TRANSPARENCY_BITS

# Masks
LAYER_MASK = (1 << LAYER_BITS) - 1
TRANSPARENCY_MASK = 1  # Only 1 bit
DISTANCE_MASK = (1 << DISTANCE_BITS) - 1
MATERIAL_MASK = (1 << MATERIAL_BITS) - 1
MESH_MASK = (1 << MESH_BITS) - 1
TRANSFORM_MASK = (1 << TRANSFORM_BITS) - 1
RENDER_MODE_MASK = (1 << RENDER_MODE_BITS) - 1

# Input buffer names
SHADER_INPUT_VERTEX = "in_vert"
SHADER_INPUT_NORMAL = "in_normal"
SHADER_INPUT_COLOR = "in_color"
SHADER_INPUT_JOINT = "in_joint"
SHADER_INPUT_WEIGHT = "in_weight"
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

# Meshes
MESH_RENDER_MODE_POINTS = 0x0000     # Value from ModernGL -> also matches OpenGL
MESH_RENDER_MODE_LINES = 0x0001      # Value from ModernGL -> also matches OpenGL
MESH_RENDER_MODE_TRIANGLES = 0x0004  # Value from ModernGL -> also matches OpenGL
MESH_RENDER_MODES = {
    "points": MESH_RENDER_MODE_POINTS,
    "lines": MESH_RENDER_MODE_LINES,
    "triangles": MESH_RENDER_MODE_TRIANGLES
}

# Debug Meshes
DEBUG_MESH_TYPE_SPHERES = 0
DEBUG_MESH_TYPE_BOX_WIREFRAME = 1
DEBUG_MESH_TYPE_TRANSFORM = 2
DEBUG_MESH_RENDER_MODES = {
    "sphere": MESH_RENDER_MODE_POINTS,
    "lines": MESH_RENDER_MODE_LINES,
    "triangles": MESH_RENDER_MODE_TRIANGLES
}

# Font Library
FONT_DEFAULT_NAME = "Consolas.ttf"
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
#                              Overlay 2D
# =============================================================================

OVERLAY_2D_NUM_COMMAND_COLUMNS = 14
OVERLAY_2D_MAX_DRAW_COMMANDS = 2048
OVERLAY_2D_VBO_SIZE_RESERVE = OVERLAY_2D_MAX_DRAW_COMMANDS * OVERLAY_2D_NUM_COMMAND_COLUMNS * 4

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
COMPONENT_TYPE_OVERLAY_2D = 6
COMPONENT_TYPE_DIRECTIONAL_LIGHT = 7
COMPONENT_TYPE_SPOT_LIGHT = 8
COMPONENT_TYPE_POINT_LIGHT = 9
COMPONENT_TYPE_COLLIDER = 10
COMPONENT_TYPE_GIZMO_3D = 11
COMPONENT_TYPE_ROBOT = 12
COMPONENT_TYPE_DEBUG_MESH = 13
COMPONENT_TYPE_SKELETON = 14
COMPONENT_TYPE_MULTI_TRANSFORM_3D = 15

# Universal arguments for all components
COMPONENT_ARG_RESOURCE_ID = "resource_id"

# Mesh Component Arguments
COMPONENT_ARG_MESH_SHAPE = "shape"
COMPONENT_ARG_MESH_FPATH = "fpath"

MESH_SHAPE_BOX = "box"
MESH_SHAPE_ICOSPHERE = "icosphere"
MESH_SHAPE_CAPSULE = "capsule"
MESH_SHAPE_CYLINDER = "cylinder"
MESH_SHAPE_FROM_OBJ = "obj"  # TODO: Kinda of a hack. You need to add argument "fpath"
MESH_SHAPE_FROM_GLTF = "gltf"

COLLIDER_SHAPE_SPHERE = "sphere"
COLLIDER_SHAPE_CAPSULE = "capsule"
COLLIDER_SHAPE_PLANE = "plane"

# =============================================================================
#                               Materials
# =============================================================================

MATERIAL_COLOR_BLACK = (0.0, 0.0, 0.0)
MATERIAL_COLOR_WHITE = (1.0, 1.0, 1.0)
MATERIAL_COLOR_RED = (1.0, 0.0, 0.0)
MATERIAL_COLOR_GREEN = (0.0, 1.0, 0.0)
MATERIAL_COLOR_BLUE = (0.0, 0.0, 1.0)
MATERIAL_COLOR_ORANGE = (1.0, 0.65, 0.0)
MATERIAL_COLOR_YELLOW = (1.0, 1.0, 0.0)
MATERIAL_COLOR_CYAN = (0.0, 1.0, 1.0)  # Also known as Aqua
MATERIAL_COLOR_MAGENTA = (1.0, 0.0, 1.0)  # Also known as Fuchsia
MATERIAL_COLOR_SILVER = (192.0 / 255.0, 192.0 / 255.0, 192.0 / 255.0)
MATERIAL_COLOR_GRAY = (128.0 / 255.0, 128.0 / 255.0, 128.0 / 255.0)
MATERIAL_COLOR_MAROON = (128.0 / 255.0, 0.0, 0.0)
MATERIAL_COLOR_OLIVE = (128.0 / 255.0, 128.0 / 255.0, 0.0)
MATERIAL_COLOR_PURPLE = (128.0 / 255.0, 0.0, 128.0 / 255.0)
MATERIAL_COLOR_TEAL = (0.0, 128.0 / 255.0, 128.0 / 255.0)
MATERIAL_COLOR_NAVY = (0.0, 0.0, 128.0 / 255.0)


# From: https://stackoverflow.com/questions/64369710/what-are-the-hex-codes-of-matplotlib-tab10-palette
MATERIAL_COLOR_TAB10_BLUE = (31 / 255.0, 119 / 255.0, 180 / 255.0)  # #1f77b4
MATERIAL_COLOR_TAB10_ORANGE = (255 / 255.0, 127 / 255.0, 14 / 255.0)  # #ff7f0e
MATERIAL_COLOR_TAB10_GREEN = (44 / 255.0, 160 / 255.0, 44 / 255.0)  # #2ca02c
MATERIAL_COLOR_TAB10_RED = (214 / 255.0, 39 / 255.0, 40 / 255.0)  # #d62728
MATERIAL_COLOR_TAB10_PURPLE = (148 / 255.0, 103 / 255.0, 189 / 255.0)  # #9467bd
MATERIAL_COLOR_TAB10_BROWN = (140 / 255.0, 86 / 255.0, 75 / 255.0)  # #8c564b
MATERIAL_COLOR_TAB10_PINK = (227 / 255.0, 119 / 255.0, 194 / 255.0)  # #e377c2
MATERIAL_COLOR_TAB10_GRAY = (127 / 255.0, 127 / 255.0, 127 / 255.0)  # #7f7f7f
MATERIAL_COLOR_TAB10_OLIVE = (188 / 255.0, 189 / 255.0, 34 / 255.0)  # #bcbd22
MATERIAL_COLOR_TAB10_CYAN = (23 / 255.0, 190 / 255.0, 207 / 255.0)  # #17becf

MATERIAL_COLORS = {
    "black": MATERIAL_COLOR_BLACK,
    "white": MATERIAL_COLOR_WHITE,
    "red": MATERIAL_COLOR_RED,
    "green": MATERIAL_COLOR_GREEN,
    "blue": MATERIAL_COLOR_BLUE,
    "orange": MATERIAL_COLOR_ORANGE,
    "yellow": MATERIAL_COLOR_YELLOW,
    "cyan": MATERIAL_COLOR_CYAN,  # Also known as Aqua
    "aqua": MATERIAL_COLOR_CYAN,  # Also known as Cyan
    "magenta": MATERIAL_COLOR_MAGENTA,  # Also known as Fuchsia
    "fuchsia": MATERIAL_COLOR_MAGENTA,  # Also known as Magenta
    "silver": MATERIAL_COLOR_SILVER,
    "gray": MATERIAL_COLOR_GRAY,
    "maroon": MATERIAL_COLOR_MAROON,
    "olive": MATERIAL_COLOR_OLIVE,
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

TRANSFORM_3D_UP_VECTOR = np.array((0, 1, 0), dtype=np.float32)
TRANSFORM_3D_COORDINATE_MODE_LOCAL = "local"
TRANSFORM_3D_COORDINATE_MODE_GLOBAL = "global"
TRANSFORM_3D_ROTATION_MODE_QUATERNION = "quaternion"
TRANSFORM_3D_ROTATION_MODE_EULER_XYZ = "euler_xyz"
TRANSFORM_3D_ROTATION_MODE_AXIS = "axis"

# =============================================================================
#                              Shader Library
# =============================================================================
SHADER_TYPE_VERTEX = "vertex"
SHADER_TYPE_GEOMETRY = "geometry"
SHADER_TYPE_FRAGMENT = "fragment"

SHADER_LIBRARY_YAML_KEY_DEFINE = "define"  # For extra definitions
SHADER_LIBRARY_YAML_KEY_VARYINGS = "varyings"  # For varying variables (those who output to VBos rather than textures)
SHADER_LIBRARY_YAML_KEY_INPUT_TEXTURE_LOCATIONS = "input_texture_locations"
SHADER_LIBRARY_YAML_KEY_EXTRA_DEFINITIONS = "extra_definitions"
SHADER_LIBRARY_FILE_EXTENSION = ".glsl"
SHADER_LIBRARY_PROGRAM_DEFINITION_EXTENSION = ".yaml"

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

FONT_LIBRARY_COLUMN_INDEX_OFFSET_X = 0
FONT_LIBRARY_COLUMN_INDEX_OFFSET_Y = 1
FONT_LIBRARY_COLUMN_INDEX_WIDTH = 2
FONT_LIBRARY_COLUMN_INDEX_HEIGHT = 3
FONT_LIBRARY_COLUMN_INDEX_U_MIN = 4
FONT_LIBRARY_COLUMN_INDEX_V_MIN = 5
FONT_LIBRARY_COLUMN_INDEX_U_MAX = 6
FONT_LIBRARY_COLUMN_INDEX_V_MAX = 7
FONT_LIBRARY_COLUMN_INDEX_VERTICAL_OFFSET = 8
FONT_LIBRARY_COLUMN_INDEX_HORIZONTAL_ADVANCE = 9

# =============================================================================
#                               Transforms
# =============================================================================

ROTATION_XYZ = 0
