import struct

import ModernGL
from PyQt5 import QtCore, QtOpenGL, QtWidgets


class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        self.timer = QtCore.QElapsedTimer()
        self.timer.restart()
        super(QGLControllerWidget, self).__init__(fmt, None)

    def initializeGL(self):
        self.ctx = ModernGL.create_context()

        prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 vert;

                in vec3 vert_color;
                out vec3 frag_color;

                uniform vec2 scale;
                uniform float rotation;

                void main() {
                    frag_color = vert_color;
                    mat2 rot = mat2(
                        cos(rotation), sin(rotation),
                        -sin(rotation), cos(rotation)
                    );
                    gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
                }
            '''),
            fragment_shader='''
                #version 330

                in vec3 frag_color;
                out vec4 color;

                void main() {
                    color = vec4(frag_color, 1.0);
                }
            '''),
        ])

        self.scale = prog.uniforms['scale']
        self.rotation = prog.uniforms['rotation']

        vbo = self.ctx.buffer(struct.pack(
            '15f',
            1.0, 0.0, 1.0, 0.0, 0.0,
            -0.5, 0.86, 0.0, 1.0, 0.0,
            -0.5, -0.86, 0.0, 0.0, 1.0,
        ))

        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])

    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.ctx.clear(0.9, 0.9, 0.9)
        self.scale.value = (self.height() / self.width() * 0.75, 0.75)
        self.rotation.value = self.timer.elapsed() / 1000
        self.vao.render()
        self.ctx.finish()
        self.update()


app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
app.exec_()
