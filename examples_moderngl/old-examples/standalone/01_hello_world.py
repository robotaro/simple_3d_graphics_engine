"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import ModernGL
# from PIL import Image

# # Context

# ctx = ModernGL.create_standalone_context()

# # Framebuffer

# size = (512, 512)
# color_rbo = ctx.renderbuffer(size)
# depth_rbo = ctx.depth_renderbuffer(size)
# fbo = ctx.framebuffer(color_rbo, depth_rbo)

# fbo.use()

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

# ctx.clear(0.9, 0.9, 0.9)
# vao.render()

# img = Image.frombytes('RGB', size, fbo.read())
# img = img.transpose(Image.FLIP_TOP_BOTTOM)
# img.save('01_hello_world.png')
