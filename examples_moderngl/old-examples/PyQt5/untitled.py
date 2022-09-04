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

        prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 vert;

                void main() {
                    gl_Position = vec4(vert, 0.0, 1.0);
                }
            '''),
            fragment_shader='''
                #version 330

                out vec4 color;

                void main() {
                    color = vec4(0.30, 0.50, 1.00, 1.0);
                }
            '''),
        ])

        vbo = self.ctx.buffer(struct.pack(
            '8f',
            -0.5, -0.5,
            -0.5, 0.5,
            0.5, -0.5,
            0.5, 0.5,
        ))

        ibo = self.ctx.buffer(struct.pack(
            '6i',
            0, 1, 2,    # triangle 1
            1, 2, 3,    # triangle 2
        ))

        content = [
            (vbo, '2f', ['vert']),
        ]

        self.vao = self.ctx.vertex_array(prog, content, ibo)

    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.ctx.clear(0.9, 0.9, 0.9)
        self.vao.render()
        self.ctx.finish()


app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
app.exec_()
