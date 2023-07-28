from core.window import Window

def demo_gui():

    window = Window(window_size=(1024, 768), window_title="GUI Demo", imgui_enabled=False)

    window.run()


if __name__ == "__main__":
    demo_gui()
