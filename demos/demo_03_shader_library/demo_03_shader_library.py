import os
import numpy as np

from core.window import Window
from core.shader_library import ShaderLibrary


class BasicScene(Window):

    DEMO_DIRECTORY = os.path.dirname(__file__)
    PROGRAM_CONFIG_FPATH = os.path.join(DEMO_DIRECTORY, "programs.yaml")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shader_library = ShaderLibrary(context=self.context,
                                            shader_directory=BasicScene.DEMO_DIRECTORY,
                                            shader_programs_config_fpath=BasicScene.PROGRAM_CONFIG_FPATH)
        self.program = self.shader_library.get_program("demo_03")
        self.vbo = None
        self.vao = None

    def setup(self):

        # Point coordinates are put followed by the vec3 color values
        vertices = np.array([
            # x, y, red, green, blue
            0.0, 0.8, 1.0, 0.0, 0.0,
            -0.6, -0.8, 0.0, 1.0, 0.0,
            0.6, -0.8, 0.0, 0.0, 1.0,
        ], dtype='f4')

        self.vbo = self.context.buffer(vertices)

        self.vao = self.context.vertex_array(
            self.program,
            [
                # Map in_vert to the first 2 floats
                # Map in_color to the next 3 floats
                (self.vbo, '2f 3f', 'in_vert', 'in_color')
            ],
        )

    def update(self, delta_time: float):
        pass

    def render(self):
        self.context.clear(1.0, 1.0, 1.0)
        self.vao.render()


def main():

    # xml_fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\scenes\default_scene.xml"
    # loader = SceneLoader()
    # new_scene = loader.load(scene_xml_fpath=xml_fpath)

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Shader Library demo",
        vertical_sync=True,
        imgui_enabled=False
    )

    app.run()

if __name__ == "__main__":
    main()
