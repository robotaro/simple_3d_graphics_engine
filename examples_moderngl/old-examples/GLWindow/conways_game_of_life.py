"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import numpy

# import GLWindow
# import ModernGL

# # This example is not working with NPOT Textures

# pixels = numpy.round(numpy.random.rand(512, 512)).astype('float32')
# grid = numpy.dstack(numpy.mgrid[0:512, 0:512][::-1] / 512).astype('float32')

# wnd = GLWindow.create_window(512, 512)
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;
#         out vec2 text;

#         void main() {
#             text = vert;
#             gl_Position = vec4((vert * 2.0 - 1.0) * 1, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform sampler2D Texture;

#         in vec2 text;
#         out vec4 color;

#         void main() {
#             color = texture(Texture, text);
#         }
#     '''),
# ])

# trans = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform sampler2D Texture;

#         in vec2 text;
#         out float vert;

#         #define LIVING 0.0
#         #define DEAD 1.0

#         #define DX 1.0 / 512.0
#         #define DY 1.0 / 512.0

#         void main() {
#             bool living = texture(Texture, text).r < 0.5;

#             int neighbours = 0;
#             if (texture(Texture, text + vec2(-DX, -DY)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(-DX, 0.0)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(-DX, DY)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(DX, -DY)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(DX, 0.0)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(DX, DY)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(0.0, DY)).r < 0.5) neighbours++;
#             if (texture(Texture, text + vec2(0.0, -DY)).r < 0.5) neighbours++;

#             if (living) {
#                 vert = (neighbours == 2 || neighbours == 3) ? LIVING : DEAD;
#             } else {
#                 vert = (neighbours == 3) ? LIVING : DEAD;
#             }
#         }
#     '''),
#     varyings=['vert']
# )

# texture = ctx.texture((512, 512), 1, pixels.tobytes(), floats=True)
# texture.filter = ModernGL.NEAREST
# texture.swizzle = 'RRR1'
# texture.use()

# vbo = ctx.buffer(struct.pack('8f', 0, 0, 0, 1, 1, 0, 1, 1))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# text = ctx.buffer(grid.tobytes())
# tao = ctx.simple_vertex_array(trans, text, ['text'])
# pbo = ctx.buffer(reserve=pixels.nbytes)

# while wnd.update():
#     ctx.viewport = wnd.viewport

#     tao.transform(pbo)
#     texture.write(pbo)

#     vao.render(ModernGL.TRIANGLE_STRIP)
