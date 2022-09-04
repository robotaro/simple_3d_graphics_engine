"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import ModernGL
# import pyglet

# wnd = pyglet.window.Window(1280, 720)
# ctx = ModernGL.create_context()

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


# def update(dt):
#     ctx.viewport = (0, 0, wnd.width, wnd.height)
#     ctx.clear(0.9, 0.9, 0.9)
#     ctx.enable(ModernGL.BLEND)
#     window_size.value = (wnd.width, wnd.height)
#     vao.render()


# pyglet.clock.schedule_interval(update, 1.0 / 60.0)
# pyglet.app.run()
