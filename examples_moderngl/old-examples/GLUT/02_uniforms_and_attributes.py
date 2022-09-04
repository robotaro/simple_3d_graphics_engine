"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import sys

# import ModernGL
# from OpenGL.GLUT import (
#     GLUT_DEPTH, GLUT_DOUBLE, GLUT_ELAPSED_TIME, GLUT_RGB, GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH, glutCreateWindow,
#     glutDisplayFunc, glutGet, glutIdleFunc, glutInit, glutInitDisplayMode, glutInitWindowSize, glutMainLoop,
#     glutSwapBuffers
# )

# glutInit(sys.argv)
# glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
# glutInitWindowSize(800, 600)
# glutCreateWindow(b'Uniforms and Attributes')

# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 in_vert;
#         in vec3 in_color;

#         out vec3 v_color;

#         uniform vec2 Scale;
#         uniform float Rotation;

#         void main() {
#             v_color = in_color;
#             mat2 rot = mat2(
#                 cos(Rotation), sin(Rotation),
#                 -sin(Rotation), cos(Rotation)
#             );
#             gl_Position = vec4((rot * in_vert) * Scale, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         in vec3 v_color;
#         out vec4 f_color;

#         void main() {
#             f_color = vec4(v_color, 1.0);
#         }
#     '''),
# ])

# rotation = prog.uniforms['Rotation']
# scale = prog.uniforms['Scale']

# vbo = ctx.buffer(struct.pack(
#     '15f',

#     1.0, 0.0,
#     1.0, 0.0, 0.0,

#     -0.5, 0.86,
#     0.0, 1.0, 0.0,

#     -0.5, -0.86,
#     0.0, 0.0, 1.0,
# ))

# vao = ctx.simple_vertex_array(prog, vbo, ['in_vert', 'in_color'])


# def display():
#     width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
#     elapsed = glutGet(GLUT_ELAPSED_TIME) / 1000.0

#     ctx.clear(0.9, 0.9, 0.9)
#     scale.value = (height / width * 0.75, 0.75)
#     rotation.value = elapsed
#     vao.render()

#     glutSwapBuffers()


# glutDisplayFunc(display)
# glutIdleFunc(display)
# glutMainLoop()
