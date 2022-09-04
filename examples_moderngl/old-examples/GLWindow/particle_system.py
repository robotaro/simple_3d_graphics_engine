"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import math
# import random
# import struct

# import GLWindow
# import ModernGL

# # Window & Context

# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# tvert = ctx.vertex_shader('''
#     #version 330

#     uniform vec2 acc;

#     in vec2 in_pos;
#     in vec2 in_prev;

#     out vec2 out_pos;
#     out vec2 out_prev;

#     void main() {
#         out_pos = in_pos * 2.0 - in_prev + acc;
#         out_prev = in_pos;
#     }
# ''')

# vert = ctx.vertex_shader('''
#     #version 330

#     in vec2 vert;

#     void main() {
#         gl_Position = vec4(vert, 0.0, 1.0);
#     }
# ''')

# frag = ctx.fragment_shader('''
#     #version 330

#     out vec4 color;

#     void main() {
#         color = vec4(0.30, 0.50, 1.00, 1.0);
#     }
# ''')

# prog = ctx.program(vert, frag])

# transform = ctx.program(tvert, ['out_pos', 'out_prev'])


# def particle():
#     a = random.uniform(0.0, math.pi * 2.0)
#     r = random.uniform(0.0, 0.001)

#     return struct.pack('2f2f', 0.0, 0.0, math.cos(a) * r - 0.003, math.sin(a) * r - 0.008)


# vbo1 = ctx.buffer(b''.join(particle() for i in range(1024)))
# vbo2 = ctx.buffer(reserve=vbo1.size)

# vao1 = ctx.simple_vertex_array(transform, vbo1, ['in_pos', 'in_prev'])
# vao2 = ctx.simple_vertex_array(transform, vbo2, ['in_pos', 'in_prev'])

# render_vao = ctx.vertex_array(prog, [
#     (vbo1, '2f8x', ['vert']),
# ])

# transform.uniforms['acc'].value = (0, -0.0001)

# idx = 0

# ctx.point_size = 5.0

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)

#     for i in range(8):
#         vbo1.write(particle(), offset=idx * struct.calcsize('2f2f'))
#         idx = (idx + 1) % 1024

#     render_vao.render(ModernGL.POINTS, 1024)
#     vao1.transform(vbo2, ModernGL.POINTS, 1024)
#     ctx.copy_buffer(vbo1, vbo2)
