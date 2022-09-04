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
#         in vec2 pos;
#         in float scale;
#         in vec3 color;

#         out vec3 v_color;

#         void main() {
#             v_color = color;
#             gl_Position = vec4(pos + vert * scale, 0.0, 1.0);
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

# # Vertex coordinates stored in vbo1
# #
# #     B------D
# #     |      |
# #     A------C

# vbo1 = ctx.buffer(struct.pack(
#     '8f',
#     -0.5, -0.5,
#     -0.5, 0.5,
#     0.5, -0.5,
#     0.5, 0.5,
# ))

# # Vertex colors stored in vbo2
# #
# #     A, B are green
# #     C, D are blue

# vbo2 = ctx.buffer(struct.pack(
#     '12f',
#     0.0, 1.0, 0.0,
#     0.0, 1.0, 0.0,
#     0.0, 0.0, 1.0,
#     0.0, 0.0, 1.0,
# ))

# # (Per instance) positions and scales stored in vbo3
# # There are 8 (position, scale) pairs

# vbo3 = ctx.buffer(struct.pack(
#     '24f',
#     0.5, 0.0, 0.3,
#     0.35, 0.35, 0.2,
#     0.0, 0.5, 0.3,
#     -0.35, 0.35, 0.2,
#     -0.5, 0.0, 0.3,
#     -0.35, -0.35, 0.2,
#     0.0, -0.5, 0.3,
#     0.35, -0.35, 0.2,
# ))

# # Index buffer (also called element buffer)
# # There are 2 trianges to render
# #
# #     A, B, C
# #     B, C, D

# ibo = ctx.buffer(struct.pack('6i', 0, 1, 2, 1, 2, 3))

# # The vao_content is a list of 3-tuples (buffer, format, attribs)
# # the format can have an empty or '/v', '/i', '/r' ending.
# # '/v' attributes are the default
# # '/i` attributes are per instance attributes
# # '/r' attributes are default values for the attributes (per render attributes)

# vao_content = [
#     (vbo1, '2f', ['vert']),
#     (vbo2, '3f', ['color']),
#     (vbo3, '2f1f/i', ['pos', 'scale']),
# ]

# vao = ctx.vertex_array(prog, vao_content, ibo)

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render(instances=8)
