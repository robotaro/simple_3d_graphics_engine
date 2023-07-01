from window.window_glfw_imgui import WindowGLFWImGUI
import imgui


class DemoImGUI(WindowGLFWImGUI):

    def setup(self):
        pass

    def render(self):
        # start new frame context
        imgui.new_frame()

        # open new window context
        imgui.begin("Your first window!", True)

        # draw text label inside of current window
        imgui.text("Hello world!")

        # close current window context
        imgui.end()


def main():

    app = DemoImGUI(window_size=(800, 600),
                    window_title="ImGUI Demo",
                    vertical_sync=True)
    app.run()


if __name__ == "__main__":
    main()
