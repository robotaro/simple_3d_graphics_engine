import struct
import numpy as np
import moderngl as mgl
from core.window_glfw import WindowGLFW


def main():
    window = WindowGLFW(window_size=(800, 600),
                        window_title="First Window - A Simple Triangle",
                        vertical_sync=True)

    context = mgl.create_context()

    prog = context.program(
        vertex_shader='''
                   #version 330

                   in vec2 in_vert;

                   in vec3 in_color;
                   out vec3 v_color;    // Goes to the fragment shader

                   void main() {
                       gl_Position = vec4(in_vert, 0.0, 1.0);
                       v_color = in_color;
                   }
               ''',
        fragment_shader='''
                   #version 330

                   in vec3 v_color;
                   out vec4 f_color;

                   void main() {
                       // We're not interested in changing the alpha value
                       f_color = vec4(v_color, 1.0);
                   }
               ''',
    )

    # Point coordinates are put followed by the vec3 color values
    vertices = np.array([
        # x, y, red, green, blue
        0.0, 0.8, 1.0, 0.0, 0.0,
        -0.6, -0.8, 0.0, 1.0, 0.0,
        0.6, -0.8, 0.0, 0.0, 1.0,
    ], dtype='f4')

    vbo = context.buffer(vertices)

    # We control the 'in_vert' and `in_color' variables
    vao = context.vertex_array(
        prog,
        [
            # Map in_vert to the first 2 floats
            # Map in_color to the next 3 floats
            (vbo, '2f 3f', 'in_vert', 'in_color')
        ],
    )

    while not window.should_close():
        window.pool_events()

        context.clear(0.0, 0.0, 0.0)
        vao.render()

        window.swap_buffers()
    window.terminate()

if __name__ == "__main__":
    main()
