from core.window import Window
import imgui


class DemoImGUI(Window):

    def setup(self):
        pass

    def update(self):

        imgui.new_frame()

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

        imgui.end()

        imgui.end_frame()

    def render(self):
        pass


def main():

    app = DemoImGUI(window_size=(800, 600),
                    window_title="ImGUI Demo",
                    vertical_sync=True,
                    imgui_enabled=True)

    app.run()


if __name__ == "__main__":
    main()
