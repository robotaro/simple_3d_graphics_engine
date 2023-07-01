import struct
import numpy as np
import moderngl as mgl
from core.window_glfw_imgui import WindowGLFWImGUI


def main():

    app = WindowGLFWImGUI(window_size=(800, 600),
                          window_title="ImGUI Demo",
                          vertical_sync=True)
    app.run()


if __name__ == "__main__":
    main()
