"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import GLWindow
# import ModernGL
# import numpy as np

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in float value;

#         void main() {
#             float x = gl_VertexID / 400.0;
#             float y = value / 200.0;

#             gl_Position = vec4(x * 2.0 - 1.0, y, 0.0, 1.0);
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

# data = np.random.geometric(0.05, 400).astype(np.float32)
# vbo = ctx.buffer(data, dynamic=True)

# vao = ctx.simple_vertex_array(prog, vbo, ['value'])

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)

#     data = np.roll(data, -1)
#     vbo.write(data)

#     vao.render(ModernGL.LINE_STRIP)
