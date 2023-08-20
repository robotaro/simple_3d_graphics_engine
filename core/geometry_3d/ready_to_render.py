import moderngl
import numpy as np
from core.shader_library import ShaderLibrary

"""
These meshes are designed to be created with the taget program you have in mind, so
make sure to set the right GLSL variable names
"""


def quad_2d(context: moderngl.Context,
            shader_library: ShaderLibrary,
            vertices_glsl_name="in_position",
            uvs_glsl_name="in_uv",
            size=(2.0, 2.0),
            position=(-1.0, -1.0)) -> dict:

    width, height = size
    xpos, ypos = position

    # fmt: off
    vertices = np.array([
        xpos, ypos + height, 0.0,
        xpos, ypos, 0.0,
        xpos + width, ypos, 0.0,
        xpos, ypos + height, 0.0,
        xpos + width, ypos, 0.0,
        xpos + width, ypos + height, 0.0,
    ], dtype=np.float32)

    uvs = np.array([
        0.0, 1.0,
        0.0, 0.0,
        1.0, 0.0,
        0.0, 1.0,
        1.0, 0.0,
        1.0, 1.0,
    ], dtype=np.float32)

    # Create VBOs
    vbo_vertices = context.buffer(vertices.astype("f4").tobytes())
    vbo_uvs = context.buffer(uvs.astype("f4").tobytes())

    return {
        "vbo_vertices": vbo_vertices,
        "vbo_uvs": vbo_uvs,
        "vao": context.vertex_array(
                shader_library["texture"],
                [
                    (vbo_vertices, '3f', vertices_glsl_name),
                    (vbo_uvs, '2f', uvs_glsl_name)
                ],
            )
        }
