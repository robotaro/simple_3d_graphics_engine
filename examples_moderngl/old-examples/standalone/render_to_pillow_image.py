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

#         in vec2 vert;
#         out vec2 tex;

#         void main() {
#             gl_Position = vec4(vert, 0.0, 1.0);
#             tex = vert / 2.0;
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         in vec2 tex;
#         out vec4 color;

#         void main() {
#             vec2 z = tex;

#             int i;
#             for(i = 0; i < 100; i++) {
#                 vec2 v = vec2((z.x * z.x - z.y * z.y), (z.y * z.x + z.x * z.y)) - vec2(0.64, -0.47);
#                 if (dot(v, v) > 4.0) break;
#                 z = v;
#             }

#             float cm = fract((i == 100 ? 0.0 : float(i)) * 10.0 / 100);
#             color = vec4(fract(cm + 0.0 / 3.0), fract(cm + 1.0 / 3.0), fract(cm + 2.0 / 3.0), 1.0);
#         }
#     ''')
# ])

# vbo = ctx.buffer(struct.pack('8f', -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# vao.render(ModernGL.TRIANGLE_STRIP)

# img = Image.frombytes('RGB', render_size, fbo.read())
# img = img.transpose(Image.FLIP_TOP_BOTTOM)
# img = img.resize(image_size, Image.LANCZOS)
# img.save('Fractal.png')
