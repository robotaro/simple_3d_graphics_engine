"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import GLWindow
# import ModernGL

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# vert = ctx.vertex_shader('''
#     #version 330

#     in vec2 vert;
#     out vec2 tex;

#     void main() {
#         gl_Position = vec4(vert, 0.0, 1.0);
#         tex = vert / 2.0 + vec2(0.5, 0.5);
#     }
# ''')

# frag = ctx.fragment_shader('''
#     #version 330

#     in vec2 tex;
#     out vec4 color;

#     uniform vec2 center;
#     uniform int iter;

#     void main() {
#         vec2 z = vec2(5.0 * (tex.x - 0.5), 3.0 * (tex.y - 0.5));
#         vec2 c = center;

#         int i;
#         for(i = 0; i < iter; i++) {
#             vec2 v = vec2(
#                 (z.x * z.x - z.y * z.y) + c.x,
#                 (z.y * z.x + z.x * z.y) + c.y
#             );
#             if (dot(v, v) > 4.0) break;
#             z = v;
#         }

#         float cm = fract((i == iter ? 0.0 : float(i)) * 10 / iter);
#         color = vec4(
#             fract(cm + 0.0 / 3.0),
#             fract(cm + 1.0 / 3.0),
#             fract(cm + 2.0 / 3.0),
#             1.0
#         );
#     }
# ''')

# prog = ctx.program(vert, frag])

# vbo = ctx.buffer(struct.pack('8f', -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# prog.uniforms['iter'].value = 100

# x, y = (0.49, 0.32)

# wnd.grab_mouse(True)

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)
#     mx, my = wnd.mouse_delta
#     x -= mx / 100
#     y -= my / 100

#     prog.uniforms['center'].value = (y, x)
#     vao.render(ModernGL.TRIANGLE_STRIP)
