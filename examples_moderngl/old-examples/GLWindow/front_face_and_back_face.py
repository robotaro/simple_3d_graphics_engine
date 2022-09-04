"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import GLWindow
# import ModernGL

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;

#         void main() {
#             gl_Position = vec4(vert, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         out vec4 color;

#         void main() {
#             color = vec4(0.3, 0.5, 1.0, 1.0);
#         }
#     '''),
# ])

# vbo = ctx.buffer(struct.pack(
#     '12f',
#     -0.5, -0.5,
#     -0.5, 0.5,
#     0.5, -0.5,
#     -0.5, 0.5,
#     0.5, -0.5,
#     0.5, 0.5,
# ))

# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# ctx.enable(ModernGL.CULL_FACE)

# while wnd.update():
#     if wnd.time % 1.0 < 0.5:
#         ctx.front_face = 'CW'
#     else:
#         ctx.front_face = 'CCW'

#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render()
