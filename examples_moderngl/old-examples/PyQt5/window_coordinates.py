import struct

import ModernGL
from PyQt5 import QtOpenGL, QtWidgets


class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)

    def initializeGL(self):
        self.ctx = ModernGL.create_context()

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
            '''),
            fragment_shader='''
                #version 330

                in vec3 v_color;
                out vec4 f_color;

                void main() {
                    f_color = vec4(v_color, 1.0);
                }
            '''),
        ])

        self.window_size = self.prog.uniforms['WindowSize']

        self.vbo = self.ctx.buffer(struct.pack(
            '15f',
            0.0, 100.0, 1.0, 0.0, 0.0,
            -86.0, -50.0, 0.0, 1.0, 0.0,
            86.0, -50.0, 0.0, 0.0, 1.0,
        ))

        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, ['in_vert', 'in_color'])

    def paintGL(self):
        width, height = self.width_pixels(), self.height_pixels()
        self.ctx.viewport = (0, 0, width, height)
        self.ctx.clear(0.9, 0.9, 0.9)
        self.ctx.enable(ModernGL.BLEND)
        self.window_size.value = (width, height)
        self.vao.render()


app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
app.exec_()
