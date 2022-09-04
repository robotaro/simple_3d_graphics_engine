"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import GLWindow
# import ModernGL
# from PIL import Image, ImageDraw, ImageFont

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# # Using Pillow to create a Texture

# font = ImageFont.truetype('../data/OpenSans-Regular.ttf', 120)

# msg = 'Hello World!'
# msg_size = font.getsize(msg)

# im = Image.new('RGBA', msg_size, (0, 0, 0, 0))

# draw = ImageDraw.Draw(im)
# draw.text((1, 0), msg, font=font, fill=(0, 0, 0, 255))
# del draw

# tex = ctx.texture(im.size, 4, im.tobytes())
# tex.use()

# # Shaders & Program

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform vec2 Screen;

#         in vec2 vert;
#         in vec2 texcoord;

#         out vec2 v_texcoord;

#         void main() {
#             gl_Position = vec4(vert / Screen * 2.0 - 1.0, 0.0, 1.0);
#             v_texcoord = texcoord;
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform sampler2D Texture;

#         in vec2 v_texcoord;
#         out vec4 color;

#         void main() {
#             color = texture(Texture, v_texcoord);
#         }
#     '''),
# ])

# prog.uniforms['Screen'].value = wnd.size

# # Buffer

# vbo = ctx.buffer(struct.pack(
#     '16f',
#     0, 0, 0, 0,
#     0, msg_size[1], 0, -1,
#     msg_size[0], 0, 1, 0,
#     msg_size[0], msg_size[1], 1, -1,
# ))

# # Put everything together

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'texcoord'])

# # Main loop

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     ctx.enable(ModernGL.BLEND)
#     vao.render(ModernGL.TRIANGLE_STRIP)
