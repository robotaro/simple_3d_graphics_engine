"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import sys
# import struct

# from OpenGL.GLUT import (
#     GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGB,
#     glutCreateWindow, glutDisplayFunc, glutInit, glutInitDisplayMode,
#     glutInitWindowSize, glutMainLoop, glutSwapBuffers,
# )

# import ModernGL

# glutInit(sys.argv)
# glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
# glutInitWindowSize(800, 600)
# glutCreateWindow(b'')

# ctx = ModernGL.create_context()

# vert = ctx.vertex_shader('''
#     #version 330
#     in vec2 vert;
#     void main() {
#         gl_Position = vec4(vert, 0.0, 1.0);
#     }
# ''')

# frag = ctx.fragment_shader('''
#     #version 330
#     out vec4 color;
#     void main() {
#         color = vec4(0.30, 0.50, 1.00, 1.0);
#     }
# ''')

# prog = ctx.program(vert, frag])

# vbo = ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])


# def display():
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render()
#     glutSwapBuffers()


# glutDisplayFunc(display)
# glutMainLoop()
