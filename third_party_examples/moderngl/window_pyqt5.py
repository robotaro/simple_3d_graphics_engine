import numpy as np

from qtmoderngl import QModernGLWidget
import sys

from PyQt5 import QtWidgets

from renderer_example import HelloWorld2D, PanTool


def vertices():
    x = np.linspace(-1.0, 1.0, 50)
    y = np.random.rand(50) - 0.5
    r = np.ones(50)
    g = np.zeros(50)
    b = np.zeros(50)
    a = np.ones(50)
    return np.dstack([x, y, r, g, b, a])


verts = vertices()
pan_tool = PanTool()


class MyWidget(QModernGLWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.scene = None

    def init(self):
        self.resize(512, 512)
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = HelloWorld2D(self.ctx)

    def render(self):
        self.screen.use()
        self.scene.clear()
        self.scene.plot(verts)

    def mousePressEvent(self, evt):
        pan_tool.start_drag(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseMoveEvent(self, evt):
        pan_tool.dragging(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseReleaseEvent(self, evt):
        pan_tool.stop_drag(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()


app = QtWidgets.QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec_())
