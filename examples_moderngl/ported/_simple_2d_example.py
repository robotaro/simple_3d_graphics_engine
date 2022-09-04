import _example


class Example(_example.Example):
    title = "Simple 2D Example"

    STATIC_COLOR_MODE = 0
    ATTRIB_COLOR_MODE = 1
    TEXTURE_MODE = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;
                in vec3 in_color;
                in vec2 in_text;

                out vec3 v_color;
                out vec2 v_text;

                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                    v_text = in_text;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;
                uniform int RenderMode;
                uniform vec3 Color;

                in vec3 v_color;
                in vec2 v_text;

                out vec4 f_color;

                void main() {
                    if (RenderMode == 0) {
                        f_color = vec4(Color, 1.0);
                    } else if (RenderMode == 1) {
                        f_color = vec4(v_color, 1.0);
                    } else if (RenderMode == 2) {
                        f_color = texture(Texture, v_text);
                    }
                }
            ''',
        )
