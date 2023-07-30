import struct

import moderngl
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Callback
from kivy.uix.widget import Widget


class CustomWidget(Widget):
    def __init__(self, **kwargs):
        super(CustomWidget, self).__init__(**kwargs)

        with self.canvas:
            self.ctx = moderngl.create_context()

            self.prog = self.ctx.program(
                vertex_shader='''
                    #version 330

                    uniform vec2 WindowSize;

                    in vec2 in_vert;
                    in vec3 in_color;

                    out vec3 v_color;

                    void main() {
                        v_color = in_color;
                        gl_Position = vec4(in_vert / WindowSize * 2.0, 0.0, 1.0);
                    }
                ''',
                fragment_shader='''
                    #version 330

                    in vec3 v_color;
                    out vec4 f_color;

                    void main() {
                        f_color = vec4(v_color, 1.0);
                    }
                ''',
            )

            self.window_size = self.prog.uniforms['WindowSize']

            self.vbo = self.context.buffer(struct.pack(
                '15f',
                0.0, 100.0, 1.0, 0.0, 0.0,
                -86.0, -50.0, 0.0, 1.0, 0.0,
                86.0, -50.0, 0.0, 0.0, 1.0,
            ))

            self.vao = self.context.simple_vertex_array(self.prog, self.vbo, ['in_vert', 'in_color'])

            Callback(self.draw)

    def draw(self, *args):
        self.width_pixels, self.height_pixels = Window.size
        self.context.viewport = (0, 0, self.width_pixels, self.height_pixels)
        self.context.clear(0.9, 0.9, 0.9)
        self.context.enable(ModernGL.BLEND)
        self.window_size.value = (self.width_pixels, self.height_pixels)
        self.vao.render_forward_pass()

    def ask_update(self, *args):
        self.canvas.ask_update()


class MainApp(App):
    def build(self):
        return CustomWidget()


if __name__ == '__main__':
    MainApp().run()
