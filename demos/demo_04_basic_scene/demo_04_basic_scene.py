import os

from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer
from core.light import DirectionalLight


class BasicScene(Window):

    DEMO_DIRECTORY = os.path.dirname(__file__)
    PROGRAM_CONFIG_FPATH = os.path.join(DEMO_DIRECTORY, "program_config.yaml")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shader_library = ShaderLibrary(context=self.context)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)
        self.scene = None

    def setup(self):
        light = DirectionalLight()
        pass

    def update(self):
        self.renderer.render()
        pass

    def render(self):
        pass


def main():

    # xml_fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\scenes\default_scene.xml"
    # loader = SceneLoader()
    # new_scene = loader.load(scene_xml_fpath=xml_fpath)

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Shader Library demo",
        vertical_sync=True,
        enable_imgui=False
    )

    app.run()

if __name__ == "__main__":
    main()
