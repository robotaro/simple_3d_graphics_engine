"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import math
# import struct

# import GLWindow
# import ModernGL
# import numpy as np


# def perspective(fov, ratio, near, far):
#     zmul = (-2.0 * near * far) / (far - near)
#     ymul = 1.0 / math.tan(fov * math.pi / 360.0)
#     xmul = ymul / ratio
#     return np.matrix([
#         [xmul, 0.0, 0.0, 0.0],
#         [0.0, ymul, 0.0, 0.0],
#         [0.0, 0.0, -1.0, zmul],
#         [0.0, 0.0, -1.0, 0.0],
#     ])


# def lookat(eye, target, up):
#     forward = target - eye
#     forward /= np.linalg.norm(forward)
#     side = np.cross(forward, up)
#     side /= np.linalg.norm(side)
#     upward = np.cross(side, forward)
#     upward /= np.linalg.norm(upward)

#     return np.matrix([
#         [side[0], side[1], side[2], -np.dot(eye, side)],
#         [upward[0], upward[1], upward[2], -np.dot(eye, upward)],
#         [-forward[0], -forward[1], -forward[2], np.dot(eye, forward)],
#         [0.0, 0.0, 0.0, 1.0],
#     ])


# def create_mvp(projection, modelview):
#     return np.transpose(projection @ modelview).astype('float32').tobytes()


# wnd = GLWindow.create_window()
# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform mat4 Mvp;

#         in vec3 in_vert;

#         void main() {
#             gl_Position = Mvp * vec4(in_vert, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         out vec4 f_color;

#         void main() {
#             f_color = vec4(0.0, 0.0, 0.0, 1.0);
#         }
#     ''')
# ])

# mvp = prog.uniforms['Mvp']

# grid = bytes()

# for i in range(0, 65):
#     grid += struct.pack('6f', i - 32, -32.0, 0.0, i - 32, 32.0, 0.0)
#     grid += struct.pack('6f', -32.0, i - 32, 0.0, 32.0, i - 32, 0.0)

# vbo = ctx.buffer(grid)
# vao = ctx.simple_vertex_array(prog, vbo, ['in_vert'])

# while wnd.update():
#     ctx.viewport = wnd.viewport
#     ctx.clear(0.9, 0.9, 0.9)

#     proj = perspective(45.0, wnd.size[0] / wnd.size[1], 0.1, 1000.0)
#     view = lookat(
#         np.array([80.0, 70.0, 60.0]),
#         np.array([0.0, 0.0, 0.0]),
#         np.array([0.0, 0.0, 1.0]),
#     )

#     mvp.write(create_mvp(proj, view))

#     vao.render(ModernGL.LINES, 65 * 4)
