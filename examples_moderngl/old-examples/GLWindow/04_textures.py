"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import os
# import struct

# import GLWindow
# import ModernGL
# from PIL import Image

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# # Shaders & Program

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;
#         in vec2 tex_coord;
#         out vec2 v_tex_coord;

#         uniform vec2 scale;
#         uniform float rotation;

#         void main() {
#             mat2 rot = mat2(
#                 cos(rotation), sin(rotation),
#                 -sin(rotation), cos(rotation)
#             );
#             gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
#             v_tex_coord = tex_coord;
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform sampler2D texture;

#         in vec2 v_tex_coord;
#         out vec4 color;

#         void main() {
#             color = vec4(texture2D(texture, v_tex_coord).rgb, 1.0);
#         }
#     '''),
# ])

# # Uniforms

# scale = prog.uniforms['scale']
# rotation = prog.uniforms['rotation']

# width, height = wnd.size
# scale.value = (height / width * 0.75, 0.75)

# # Buffer

# vbo = ctx.buffer(struct.pack(
#     '12f',
#     1.0, 0.0, 0.5, 1.0,
#     -0.5, 0.86, 1.0, 0.0,
#     -0.5, -0.86, 0.0, 0.0,
# ))

# # Put everything together

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'tex_coord'])

# # Texture

# img = Image.open(os.path.join(os.path.dirname(__file__), '..', 'data', 'noise.jpg'))
# texture = ctx.texture(img.size, 3, img.tobytes())
# texture.use()

# # Main loop

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     rotation.value = wnd.time
#     vao.render()
