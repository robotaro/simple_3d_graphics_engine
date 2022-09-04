import struct

import moderngl
import pygame
from pygame.locals import DOUBLEBUF, OPENGL

pygame.init()
pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

ctx = moderngl.create_context()

prog = ctx.program(
        vertex_shader='''
    #version 310 es
    in vec2 vert;
    void main() {
        gl_Position = vec4(vert, 0.0, 1.0);
    }
''',
        fragment_shader='''
    #version 310 es
    precision mediump float;
    out vec4 color;

    void main() {
        color = vec4(0.3, 0.5, 1.00, 1.0);
    }
''')


vbo = ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
vao = ctx.simple_vertex_array(prog, vbo, 'vert')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ctx.clear(0.9, 0.9, 0.9)
    vao.render()

    pygame.display.flip()
    pygame.time.wait(6)
