import GLWindow
import moderngl
from PIL import Image, ImageDraw, ImageFont
import numpy as np

wnd = GLWindow.create_window()
ctx = moderngl.create_context()

prog = ctx.program(
    vertex_shader='''
        #version 330

        in vec2 in_vert;
        in vec3 in_text;

        out vec3 v_text;

        void main() {
            v_text = in_text;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330

        uniform sampler2DArray Texture;

        in vec3 v_text;

        out vec4 f_color;

        void main() {
            f_color = texture(Texture, v_text);
        }
    ''',
)

vbo = ctx.buffer(np.array([
    (
        -0.3, -0.3 + i * 0.2 - 0.2, 0.0, 0.0, i,
        0.3, -0.3 + i * 0.2 - 0.2, 1.0, 0.0, i,
        0.0, 0.3 + i * 0.2 - 0.2, 0.5, 1.0, i,
    ) for i in range(3)
], dtype='f4'))

images = [
    Image.new('RGB', (256, 256), 'red'),
    Image.new('RGB', (256, 256), 'green'),
    Image.new('RGB', (256, 256), 'blue'),
]

merged = b''.join(img.tobytes() for img in images)

tex = ctx.texture_array((256, 256, 3), 3, merged)
tex.use()

vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_text')

while wnd.update_dimensions():
    ctx.clear(1.0, 1.0, 1.0, 1.0)
    vao.render()
