import moderngl
import numpy as np

"""
These meshes are designed to be created with the taget program you have in mind, so
make sure to set the right GLSL variable names
"""


def quad_2d(context: moderngl.Context,
            program: moderngl.Program,
            vertices_glsl_name="in_vertices",
            uvs_glsl_name="in_uvs",
            size=(1.0, 1.0),
            pos=(0.0, 0.0)) -> dict:
    """
    A Quad designed to be used as a rendering area on the screen

    Rendering Method: TRIANGLES

    :param program: ModernGL program
    :param context: ModernGL context
    :param vertices_glsl_name: str, reference inside the GLSL program for the vertices
    :param normals_glsl_name: str, reference inside the GLSL program for the normals
    :param uvs_glsl_name: str, reference inside the GLSL program for the uvs
    :param size: tuple, (width, height)
    :param pos: tuple (x, y)
    :return: Dictionary with VBOs and VAO ready to render
    """
    width, height = size
    xpos, ypos = pos

    # fmt: off
    vertices = np.array([
        xpos - width / 2.0, ypos + height / 2.0, 0.0,
        xpos - width / 2.0, ypos - height / 2.0, 0.0,
        xpos + width / 2.0, ypos - height / 2.0, 0.0,
        xpos - width / 2.0, ypos + height / 2.0, 0.0,
        xpos + width / 2.0, ypos - height / 2.0, 0.0,
        xpos + width / 2.0, ypos + height / 2.0, 0.0,
    ], dtype=np.float32)

    """normals = np.array([
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
    ], dtype=np.float32)"""

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
    #vbo_normals = context.buffer(normals.astype("f4").tobytes())
    vbo_uvs = context.buffer(uvs.astype("f4").tobytes())

    return {
        "program": program,
        "vbo_vertices": vbo_vertices,
        "vbo_uvs": vbo_uvs,
        "vao": context.vertex_array(
                program,
                [
                    (vbo_vertices, '3f', vertices_glsl_name),
                    (vbo_uvs, '2f', uvs_glsl_name)
                ],
            )
        }
