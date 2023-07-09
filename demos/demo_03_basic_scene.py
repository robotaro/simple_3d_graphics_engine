import os

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary


class BasicScene(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shader_library = ShaderLibrary(shader_directory=constants.SHADERS_DIRECTORY)
        source_code = self.shader_library.generate_source_code(shader_key="lines_instanced_positions.vs.glsl")



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
