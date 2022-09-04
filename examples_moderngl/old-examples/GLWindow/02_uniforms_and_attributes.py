"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import GLWindow
# import ModernGL

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# # Shaders & Program

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;

#         in vec3 vert_color;
#         out vec3 frag_color;

#         uniform vec2 scale;
#         uniform float rotation;

#         void main() {
#             frag_color = vert_color;
#             mat2 rot = mat2(
#                 cos(rotation), sin(rotation),
#                 -sin(rotation), cos(rotation)
#             );
#             gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         in vec3 frag_color;
#         out vec4 color;

#         void main() {
#             color = vec4(frag_color, 1.0);
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
#     '15f',

#     1.0, 0.0,
#     1.0, 0.0, 0.0,

#     -0.5, 0.86,
#     0.0, 1.0, 0.0,

#     -0.5, -0.86,
#     0.0, 0.0, 1.0,
# ))

# # Put everything together

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])

# # Main loop

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     rotation.value = wnd.time
#     vao.render()
