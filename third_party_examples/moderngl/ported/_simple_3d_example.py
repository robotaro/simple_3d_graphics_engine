from pyrr import Matrix44

import _example


class Example(_example.Example):
    title = "Simple 3D Example"

    STATIC_COLOR_MODE = 0
    STATIC_COLOR_WITH_LIGHT_MODE = 1
    ATTRIB_COLOR_WITH_LIGHT_MODE = 2
    TEXTURE_WITH_LIGHT_MODE = 3

    def set_camera(self, fov, eye, target):
        proj = Matrix44.perspective_projection(fov, self.aspect_ratio, 0.1, 1000.0)
        look = Matrix44.look_at(eye, target, (0.0, 0.0, 1.0))
        self.prog['Mvp'].write((proj * look).astype('f4').tobytes())
        self.prog['Light'].value = eye

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;

                in vec3 in_vert;
                in vec3 in_norm;
                in vec3 in_color;
                in vec2 in_text;

                out vec3 v_vert;
                out vec3 v_norm;
                out vec3 v_color;
                out vec2 v_text;

                void main() {
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                    v_vert = in_vert;
                    v_norm = in_norm;
                    v_color = in_color;
                    v_text = in_text;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;
                uniform int RenderMode;
                uniform vec3 Color;
                uniform vec3 Light;

                in vec3 v_vert;
                in vec3 v_norm;
                in vec3 v_color;
                in vec2 v_text;

                out vec4 f_color;

                void main() {
                    float lum = 0.2 + 0.8 * abs(dot(normalize(Light - v_vert), normalize(v_norm)));
                    if (RenderMode == 0) {
                        f_color = vec4(Color, 1.0);
                    } else if (RenderMode == 1) {
                        f_color = vec4(Color * lum, 1.0);
                    } else if (RenderMode == 2) {
                        f_color = vec4(v_color * lum, 1.0);
                    } else if (RenderMode == 3) {
                        f_color = texture(Texture, v_text) * vec4(lum, lum, lum, 1.0);
                    }
                }
            ''',
        )
