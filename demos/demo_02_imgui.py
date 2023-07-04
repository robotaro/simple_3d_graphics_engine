from core.window import Window
import imgui


class DemoImGUI(Window):

    def setup(self):
        pass

    def update(self):

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

    def render(self):
        pass

def main():

    app = DemoImGUI(window_size=(800, 600),
                    window_title="ImGUI Demo",
                    vertical_sync=True)
    app.run()


if __name__ == "__main__":
    main()
