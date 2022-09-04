"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import ModernGL
# import pyglet

# wnd = pyglet.window.Window()
# ctx = ModernGL.create_context()

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

# scale = prog.uniforms['scale']
# rotation = prog.uniforms['rotation']

# vbo = ctx.buffer(struct.pack(
#     '15f',

#     1.0, 0.0,
#     1.0, 0.0, 0.0,

#     -0.5, 0.86,
#     0.0, 1.0, 0.0,

#     -0.5, -0.86,
#     0.0, 0.0, 1.0,
# ))

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])


# def update(dt):
#     scale.value = (wnd.height / wnd.width * 0.75, 0.75)
#     ctx.viewport = (0, 0, wnd.width, wnd.height)
#     ctx.clear(0.9, 0.9, 0.9)
#     rotation.value += dt
#     vao.render()


# pyglet.clock.schedule_interval(update, 1.0 / 60.0)
# pyglet.app.run()
