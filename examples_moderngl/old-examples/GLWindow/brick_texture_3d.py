"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# from math import cos, sin
# from random import randrange

# import GLWindow
# import ModernGL
# from pyrr import Matrix44


# def create_brick_texture(size):
#     result = bytearray()

#     for z in range(size[2]):
#         for y in range(size[1]):
#             for x in range(size[0]):

#                 if x != size[0] - 1 and y != size[1] - 1 and z != size[2] - 1:
#                     n1, n2, n3 = randrange(0, 16), randrange(0, 16), randrange(0, 16)
#                     result += struct.pack('BBB', 220 + n1, 31 + n2, 0 + n3)

#                 else:
#                     n = randrange(0, 16)
#                     result += struct.pack('BBB', 240 - n, 240 - n, 240 - n)

#     return bytes(result)


# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform mat4 Mvp;
#         uniform vec3 TextureSize;

#         in vec3 vert;
#         out vec3 v_text;

#         void main() {
#             v_text = vert * 100.0 / TextureSize;
#             gl_Position = Mvp * vec4(vert, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform sampler3D Texture;

#         in vec3 v_text;
#         out vec4 color;

#         void main() {
#             color = texture(Texture, v_text);
#         }
#     '''),
# ])

# mvp = prog.uniforms['Mvp']
# texture_size = prog.uniforms['TextureSize']

# vbo = ctx.buffer(struct.pack(
#     '36f',

#     0.0, 0.0, 0.0,
#     2.0, 0.0, 0.0,
#     0.0, 2.0, 0.0,

#     0.0, 0.0, 0.0,
#     2.0, 0.0, 0.0,
#     0.0, 0.0, 2.0,

#     0.0, 0.0, 0.0,
#     0.0, 2.0, 0.0,
#     0.0, 0.0, 2.0,

#     2.0, 0.0, 0.0,
#     0.0, 2.0, 0.0,
#     0.0, 0.0, 2.0,
# ))

# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# size = (20, 16, 8)
# texture_size.value = size
# texure = ctx.texture3d(size, 3, create_brick_texture(size))
# texure.filter = ModernGL.NEAREST
# texure.use()

# ctx.enable(ModernGL.DEPTH_TEST)

# while wnd.update():
#     angle = wnd.time
#     width, height = wnd.size
#     proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
#     lookat = Matrix44.look_at(
#         (cos(angle) * 5.0, sin(angle) * 5.0, 2.5),
#         (0.0, 0.0, 0.5),
#         (0.0, 0.0, 1.0),
#     )

#     mvp.write((proj * lookat).astype('float32').tobytes())

#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     vao.render()
