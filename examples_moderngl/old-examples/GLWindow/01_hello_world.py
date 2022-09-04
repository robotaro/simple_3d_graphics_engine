"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import GLWindow
# import ModernGL

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# # Shaders & Program

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

# # Buffer

# vbo = ctx.buffer(struct.pack(
#     '6f',
#     0.0, 0.8,
#     -0.6, -0.8,
#     0.6, -0.8,
# ))

# # Put everything together

# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# # Main loop

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render()
