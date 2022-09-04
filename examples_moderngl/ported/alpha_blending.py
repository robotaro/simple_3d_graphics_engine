import numpy as np

import _example


class Example(_example.Example):
    title = 'Alpha Blending'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;
                in vec4 in_color;

                out vec4 v_color;

                uniform vec2 Scale;
                uniform float Rotation;

                void main() {
                    v_color = in_color;
                    float r = Rotation * (0.5 + gl_InstanceID * 0.05);
                    mat2 rot = mat2(cos(r), sin(r), -sin(r), cos(r));
                    gl_Position = vec4((rot * in_vert) * Scale, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                in vec4 v_color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(v_color);
                }
            ''',
        )

        self.prog['Scale'] = (0.5, self.aspect_ratio * 0.5)

        vertices = np.array([
            1.0, 0.0,
            1.0, 0.0, 0.0, 0.5,

            -0.5, 0.86,
            0.0, 1.0, 0.0, 0.5,

            -0.5, -0.86,
            0.0, 0.0, 1.0, 0.5,
        ])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')
        self.vao.scope = self.ctx.scope(enable=self.ctx.BLEND)
        self.vao.instances = 10

    def render(self, time: float, frame_time: float):
        self.prog['Rotation'] = time
        self.ctx.screen.clear(color=(1.0, 1.0, 1.0))
        self.vao.render()


if __name__ == '__main__':
    Example.run()
