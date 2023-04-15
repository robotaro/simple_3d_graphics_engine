import core
from core.window_glfw import WindowGLFW

def demo_gui():

    window = WindowGLFW(window_size=(1024, 768), window_title="GUI Demo")

    window.run()


if __name__ == "__main__":
    demo_gui()
