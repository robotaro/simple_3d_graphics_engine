"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct

# import ModernGL
# import pygame
# from pygame.locals import DOUBLEBUF, OPENGL
# from pyrr import Matrix44

# width, height = 1280, 720

# pygame.init()
# pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# ctx = ModernGL.create_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         uniform mat4 Mvp;

#         in vec3 in_vert;
#         in vec3 in_color;

#         out vec3 v_color;

#         void main() {
#             v_color = in_color;
#             gl_Position = Mvp * vec4(in_vert, 1.0);
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

# mvp = prog.uniforms['Mvp']

# grid = bytearray()

# for i in range(0, 32 + 1):
#     grid += struct.pack('6f', i - 16.0, -16.0, 0.0, 0.0, 0.0, 0.0)
#     grid += struct.pack('6f', i - 16.0, 16.0, 0.0, 0.0, 0.0, 0.0)
#     grid += struct.pack('6f', -16.0, i - 16.0, 0.0, 0.0, 0.0, 0.0)
#     grid += struct.pack('6f', 16.0, i - 16.0, 0.0, 0.0, 0.0, 0.0)

# vbo = ctx.buffer(grid)
# vao = ctx.simple_vertex_array(prog, vbo, ['in_vert', 'in_color'])

# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     ctx.viewport = (0, 0, width, height)
#     ctx.clear(0.9, 0.9, 0.9)
#     ctx.enable(ModernGL.DEPTH_TEST)

#     proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
#     lookat = Matrix44.look_at(
#         (40.0, 30.0, 20.0),
#         (0.0, 0.0, 0.0),
#         (0.0, 0.0, 1.0),
#     )

#     mvp.write((proj * lookat).astype('float32').tobytes())
#     vao.render(ModernGL.LINES)

#     pygame.display.flip()
#     pygame.time.wait(10)
