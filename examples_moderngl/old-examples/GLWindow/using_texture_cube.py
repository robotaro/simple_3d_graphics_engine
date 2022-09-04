"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import random

# import GLWindow
# import ModernGL

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;
#         in vec3 tex_coord;
#         out vec3 v_tex_coord;

#         void main() {
#             gl_Position = vec4(vert, 0.0, 1.0);
#             v_tex_coord = tex_coord;
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform samplerCube Texture;

#         in vec3 v_tex_coord;
#         out vec4 color;

#         void main() {
#             color = vec4(texture(Texture, v_tex_coord).rgb, 1.0);
#         }
#     '''),
# ])

# data = bytes()

# for i in range(11):
#     data += struct.pack('5f', i / 10.0 - 0.5, 0.2, random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
#     data += struct.pack('5f', i / 10.0 - 0.5, -0.2, random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))

# vbo = ctx.buffer(data)

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'tex_coord'])

# pixels = bytes()

# for i in range(4):
#     for j in range(4):
#         for k in range(6):
#             r = int(i * 255 / 3)
#             g = int(j * 255 / 3)
#             b = int(k * 255 / 5)
#             pixels += struct.pack('3B', r, g, b)

# texture = ctx.texture_cube((4, 4), 3, pixels)
# texture.use()

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render(ModernGL.TRIANGLE_STRIP)
