"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import numpy

# import GLWindow
# import ModernGL

# # This example is not working with NPOT Textures

# width, height = 640, 460

# pixels = numpy.round(numpy.random.rand(width, height)).astype('float32')
# grid = numpy.dstack(numpy.mgrid[0:height, 0:width][::-1]).astype('int32')

# wnd = GLWindow.create_window(width, height)
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
#         uniform int Width;
#         uniform int Height;

#         in ivec2 text;
#         out float vert;

#         #define LIVING 0.0
#         #define DEAD 1.0

#         bool cell(int x, int y) {
#             return texelFetch(Texture, ivec2((x + Width) % Width, (y + Height) % Height), 0).r < 0.5;
#         }

#         void main() {
#             bool living = cell(text.x, text.y);

#             int neighbours = 0;
#             if (cell(text.x - 1, text.y - 1)) neighbours++;
#             if (cell(text.x - 1, text.y + 0)) neighbours++;
#             if (cell(text.x - 1, text.y + 1)) neighbours++;
#             if (cell(text.x + 1, text.y - 1)) neighbours++;
#             if (cell(text.x + 1, text.y + 0)) neighbours++;
#             if (cell(text.x + 1, text.y + 1)) neighbours++;
#             if (cell(text.x + 0, text.y + 1)) neighbours++;
#             if (cell(text.x + 0, text.y - 1)) neighbours++;

#             if (living) {
#                 vert = (neighbours == 2 || neighbours == 3) ? LIVING : DEAD;
#             } else {
#                 vert = (neighbours == 3) ? LIVING : DEAD;
#             }
#         }
#     '''),
#     varyings=['vert']
# )

# trans.uniforms['Width'].value = width
# trans.uniforms['Height'].value = height

# texture = ctx.texture((width, height), 1, pixels.tobytes(), floats=True)
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
