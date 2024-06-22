import moderngl
import numpy as np

from src.core import constants

"""
These meshes are designed to be created with the taget program you have in mind, so
make sure to set the right GLSL variable names
"""


def quad_2d(ctx: moderngl.Context,
            program: moderngl.Program,
            size=(2.0, 2.0),
            position=(-1.0, -1.0)) -> dict:

    width, height = size
    xpos, ypos = position

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
    vbo_vertices = ctx.buffer(vertices.astype("f4").tobytes())
    vbo_uvs = ctx.buffer(uvs.astype("f4").tobytes())

    return {
        "vbo_vertices": vbo_vertices,
        "vbo_uvs": vbo_uvs,
        "vao": ctx.vertex_array(
                program,
                [
                    (vbo_vertices, '3f', constants.SHADER_INPUT_VERTEX),
                    (vbo_uvs, '2f', constants.SHADER_INPUT_UV)
                ],
            )
        }
