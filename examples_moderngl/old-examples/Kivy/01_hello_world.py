import struct

import ModernGL
from kivy.app import App
from kivy.graphics import Callback
from kivy.uix.widget import Widget


class CustomWidget(Widget):
    def __init__(self, **kwargs):
        super(CustomWidget, self).__init__(**kwargs)

        with self.canvas:

            self.ctx = ModernGL.create_context()

            self.vert = vertex_shader='''
                #version 330

                in vec2 vert;

                void main() {
                    gl_Position = vec4(vert, 0.0, 1.0);
                }
            ''')

            self.frag = fragment_shader='''
                #version 330

                out vec4 color;

                void main() {
                    color = vec4(0.30, 0.50, 1.00, 1.0);
                }
            ''')

            self.prog = self.ctx.program(self.vert, self.frag])

            self.vbo = self.ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, ['vert'])

            self.draw()

            Callback(self.draw)

    def draw(self, *args):
        self.ctx.clear(0.9, 0.9, 0.9)
        self.vao.render()

    def ask_update(self, *args):
        self.canvas.ask_update()


class MainApp(App):
    def build(self):
        return CustomWidget()


if __name__ == '__main__':
    MainApp().run()
