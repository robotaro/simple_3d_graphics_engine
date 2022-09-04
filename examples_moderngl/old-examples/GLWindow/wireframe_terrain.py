"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import os
# import struct

# import GLWindow
# import ModernGL
# from PIL import Image
# from pyrr import Matrix44

# data_folder = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# width, height = wnd.size

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform mat4 Mvp;
#         uniform sampler2D Heightmap;

#         in vec2 in_vert;
#         in vec3 in_color;

#         out vec3 v_color;

#         void main() {
#             v_color = in_color;
#             gl_Position = Mvp * vec4(in_vert.xy * 32.0 - 15.5, texture(Heightmap, in_vert.xy).r * 10.0, 1.0);
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

# mvp = prog.uniforms['Mvp']

# vertices = bytearray()
# indices = bytearray()

# for i in range(0, 32):
#     for j in range(0, 32):
#         vertices += struct.pack('2f', i / 32, j / 32)

# for i in range(0, 32 - 1):
#     for j in range(0, 32):
#         indices += struct.pack('2i', i * 32 + j, (i + 1) * 32 + j)
#     indices += struct.pack('i', -1)

# vbo = ctx.buffer(vertices)
# ibo = ctx.buffer(indices)

# vao_content = [
#     (vbo, '2f', ['in_vert']),
# ]

# img = Image.open(os.path.join(data_folder, 'noise.jpg')).convert('L')
# texture = ctx.texture(img.size, 1, img.tobytes())
# texture.use()

# vao = ctx.vertex_array(prog, vao_content, ibo)


# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     ctx.enable(ModernGL.DEPTH_TEST)
#     ctx.wireframe = True

#     proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
#     lookat = Matrix44.look_at(
#         (40.0, 30.0, 30.0),
#         (0.0, 0.0, 0.0),
#         (0.0, 0.0, 1.0),
#     )

#     mvp.write((proj * lookat).astype('float32').tobytes())
#     vao.render(ModernGL.TRIANGLE_STRIP)
