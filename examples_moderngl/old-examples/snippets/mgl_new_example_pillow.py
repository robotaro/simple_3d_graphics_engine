# """
# NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
# """

# import struct

# import ModernGL
# from PIL import Image

# ctx = ModernGL.create_standalone_context()

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

# vbo = ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# fbo = ctx.framebuffer(ctx.renderbuffer((512, 512)))

# fbo.use()
# fbo.clear(0.9, 0.9, 0.9)
# vao.render()

# pixels = fbo.read(components=3, alignment=1)
# img = Image.frombytes('RGB', fbo.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
# img.show()
