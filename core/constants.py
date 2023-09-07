import os

# Default Directories
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
SHADERS_DIRECTORY = os.path.join(RESOURCES_DIR, "shaders")
SHADER_PROGRAMS_YAML_FPATH = os.path.join(os.path.dirname(__file__), "config", "programs.yaml")

# Default OpenGL constants
OPENGL_MAJOR_VERSION = 4
OPENGL_MINOR_VERSION = 0

# Window
WINDOW_DEFAULT_SIZE = (1280, 720)
WINDOW_DEFAULT_TITLE = "Application Window"

# OpenGL Shaders
SHADER_TYPE_VERTEX = "vertex"
SHADER_TYPE_GEOMETRY = "geometry"
SHADER_TYPE_FRAGMENT = "fragment"
SHADER_TYPES = [
    SHADER_TYPE_VERTEX,
    SHADER_TYPE_GEOMETRY,
    SHADER_TYPE_FRAGMENT
]

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

BACKGROUND_COLOR_RGBA = (1.0, 1.0, 1.0, 1.0)

# Font
FONT_VERTICES_NUM_COLUMNS = 12  # 6 vertices, 2 dimensions each
FONT_UVS_NUM_COLUMNS = 12  # 6 vertices, 2 dimensions each

# Camera
CAMERA_Z_NEAR = 0.01
CAMERA_Z_FAR = 1000.0
CAMERA_ZOOM_SPEED = 0.05

# Render Flags - not yet used
RENDER_FLAG_NONE = 0  # Normal PBR Render.
RENDER_FLAG_DEPTH_ONLY = 1  # Only render the depth buffer.
RENDER_FLAG_OFFSCREEN = 2  # Render off-screen and return the depth and (optionally) color buffers.
RENDER_FLAG_FLIP_WIREFRAME = 4  # Invert the status of wireframe rendering for each mes
RENDER_FLAG_ALL_WIREFRAME = 8  # Render all meshes as wireframes.
RENDER_FLAG_ALL_SOLID = 16  # Render all meshes as solids.
RENDER_FLAG_SHADOWS_DIRECTIONAL = 32  # Render shadows for directional lights.
RENDER_FLAG_SHADOWS_POINT = 64  # Render shadows for point lights.
RENDER_FLAG_SHADOWS_SPOT = 128  # Render shadows for spot lights.
RENDER_FLAG_SHADOWS_ALL = 32 | 64 | 128  # Render shadows for all lights.
RENDER_FLAG_VERTEX_NORMALS = 256  # Render vertex normals.
RENDER_FLAG_FACE_NORMALS = 512  # Render face normals.
RENDER_FLAG_SKIP_CULL_FACES = 1024  # Do not cull back faces.
RENDER_FLAG_RGBA = 2048  # Render the color buffer with the alpha channel enabled.
RENDER_FLAG_FLAT = 4096  # Render the color buffer flat, with no lighting computations.
RENDER_FLAG_SEG = 8192

# Buffer Flags
BUFFER_FLAG_POSITION = 0
BUFFER_FLAG_NORMAL = 1
BUFFER_FLAG_TANGENT = 2
BUFFER_FLAG_TEXCOORD_0 = 4
BUFFER_FLAG_TEXCOORD_1 = 8
BUFFER_FLAG_COLOR_0 = 16
BUFFER_FLAG_JOINTS_0 = 32
BUFFER_FLAG_WEIGHTS_0 = 64

# Texture Flags
TEXTURE_FLAG_NONE = 0
TEXTURE_FLAG_NORMAL = 1
TEXTURE_FLAG_OCCLUSION = 2
TEXTURE_FLAG_EMISSIVE = 4
TEXTURE_FLAG_BASE_COLOR = 8
TEXTURE_FLAG_METALLIC_ROUGHNESS = 16
TEXTURE_FLAG_DIFFUSE = 32
TEXTURE_FLAG_SPECULAR_GLOSSINESS = 64
