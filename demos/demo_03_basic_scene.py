import os
import yaml

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer
from core.scene.scene import Scene
from core.scene.scene_loader import SceneLoader


class BasicScene(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shader_library = ShaderLibrary(context=self.context)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)
        self.scene = Scene()


def main():

    # xml_fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\scenes\default_scene.xml"
    # loader = SceneLoader()
    # new_scene = loader.load(scene_xml_fpath=xml_fpath)

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Basic Scene",
        vertical_sync=True,
        enable_imgui=False
    )

    app.run()

if __name__ == "__main__":
    main()
