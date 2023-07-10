import os
import yaml

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer


class BasicScene(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shader_library = ShaderLibrary(context=self.context)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)



def main():

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Basic Scene",
        vertical_sync=True,
        enable_imgui=False
    )


    app.run()

if __name__ == "__main__":
    main()
