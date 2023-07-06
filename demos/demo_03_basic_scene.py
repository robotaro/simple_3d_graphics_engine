import os

from core.window import Window


class BasicScene(Window):

    def __init__(self,
                 window_size: tuple,
                 window_title: str,
                 vertical_sync=True):
        super().__init__(window_size=window_size,
                         window_title=window_title,
                         vertical_sync=vertical_sync)

        self.shader_library = ShaderLibrary(mgl_context=self.context)


def main():

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Basic Scene",
        vertical_sync=True
    )

    app.run()

if __name__ == "__main__":
    main()
