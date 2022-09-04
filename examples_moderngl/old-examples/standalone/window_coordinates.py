"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import ModernGL
# from PIL import Image

# render_size = 1024, 1024
# image_size = 512, 512

# ctx = ModernGL.create_standalone_context()

# color_rbo = ctx.renderbuffer(render_size)
# depth_rbo = ctx.depth_renderbuffer(render_size)
# fbo = ctx.framebuffer(color_rbo, depth_rbo)

# fbo.use()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform vec2 WindowSize;

#         in vec2 in_vert;
#         in vec3 in_color;

#         out vec3 v_color;

#         void main() {
#             v_color = in_color;
#             gl_Position = vec4(in_vert / WindowSize * 2.0, 0.0, 1.0);
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

# window_size = prog.uniforms['WindowSize']

# vbo = ctx.buffer(struct.pack(
#     '15f',
#     0.0, 100.0, 1.0, 0.0, 0.0,
#     -86.0, -50.0, 0.0, 1.0, 0.0,
#     86.0, -50.0, 0.0, 0.0, 1.0,
# ))

# vao = ctx.simple_vertex_array(prog, vbo, ['in_vert', 'in_color'])

# width, height = render_size
# ctx.viewport = (0, 0, width, height)
# ctx.clear(0.9, 0.9, 0.9)
# ctx.enable(ModernGL.BLEND)
# window_size.value = (width, height)
# vao.render()

# img = Image.frombytes('RGB', render_size, fbo.read())
# img = img.transpose(Image.FLIP_TOP_BOTTOM)
# img = img.resize(image_size, Image.LANCZOS)
# img.save('window_coordinates.png')
