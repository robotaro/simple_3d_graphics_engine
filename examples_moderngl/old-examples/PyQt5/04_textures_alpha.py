import os
import struct

import ModernGL
from PIL import Image
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

        img = Image.open(os.path.join(os.path.dirname(__file__), '..', 'data', 'noise.jpg'))
        img = img.convert('L')

        texture = self.ctx.texture(img.size, 1, img.tobytes())
        texture.swizzle = '111R'
        texture.use()

        prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 vert;
                in vec2 tex_coord;
                out vec2 v_tex_coord;

                uniform vec2 scale;
                uniform float rotation;

                void main() {
                    mat2 rot = mat2(
                        cos(rotation), sin(rotation),
                        -sin(rotation), cos(rotation)
                    );
                    gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
                    v_tex_coord = tex_coord;
                }
            '''),
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;

                in vec2 v_tex_coord;
                out vec4 color;

                void main() {
                    color = texture(Texture, v_tex_coord);
                }
            '''),
        ])

        self.scale = prog.uniforms['scale']
        self.rotation = prog.uniforms['rotation']

        vbo = self.context.buffer(struct.pack(
            '12f',
            1.0, 0.0, 0.5, 1.0,
            -0.5, 0.86, 1.0, 0.0,
            -0.5, -0.86, 0.0, 0.0,
        ))

        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert', 'tex_coord'])

    def paintGL(self):
        self.context.viewport = (0, 0, self.width_pixels(), self.height_pixels())
        self.context.clear(0.5, 0.5, 0.5)
        self.context.enable(ModernGL.BLEND)
        self.scale.value = (self.height_pixels() / self.width_pixels() * 0.75, 0.75)
        self.rotation.value = self.timer.elapsed() / 1000
        self.vao.render()
        self.context.finish()
        self.update_dimensions()


app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
app.exec_()
