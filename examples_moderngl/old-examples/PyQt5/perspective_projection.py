import struct

from PyQt5 import QtOpenGL, QtWidgets

import ModernGL
from pyrr import Matrix44


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

                uniform mat4 Mvp;

                in vec3 in_vert;
                in vec3 in_color;

                out vec3 v_color;

                void main() {
                    v_color = in_color;
                    gl_Position = Mvp * vec4(in_vert, 1.0);
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

        self.mvp = self.prog.uniforms['Mvp']

        grid = bytearray()

        for i in range(0, 32 + 1):
            grid += struct.pack('6f', i - 16.0, -16.0, 0.0, 0.0, 0.0, 0.0)
            grid += struct.pack('6f', i - 16.0, 16.0, 0.0, 0.0, 0.0, 0.0)
            grid += struct.pack('6f', -16.0, i - 16.0, 0.0, 0.0, 0.0, 0.0)
            grid += struct.pack('6f', 16.0, i - 16.0, 0.0, 0.0, 0.0, 0.0)

        self.vbo = self.context.buffer(grid)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, ['in_vert', 'in_color'])

    def paintGL(self):
        width, height = self.width_pixels(), self.height_pixels()
        self.context.viewport = (0, 0, width, height)
        self.context.clear(0.9, 0.9, 0.9)
        self.context.enable(ModernGL.DEPTH_TEST)

        proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (40.0, 30.0, 20.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )

        self.mvp.write((proj * lookat).astype('float32').tobytes())
        self.vao.render(ModernGL.LINES)


app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
app.exec_()
