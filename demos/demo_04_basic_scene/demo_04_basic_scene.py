import os

from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer
from core.scene import Scene
from core.camera import PerspectiveCamera
from core.viewport import Viewport
from core.renderables.chessboard_plane import ChessboardPlane
from core.utilities import utils_logging
import logging


class BasicScene(Window):

    DEMO_DIRECTORY = os.path.dirname(__file__)
    PROGRAM_CONFIG_FPATH = os.path.join(DEMO_DIRECTORY, "shader_programs.yaml")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create basic structures for rendering
        self.shader_library = ShaderLibrary(context=self.context,
                                            shader_programs_config_fpath=BasicScene.PROGRAM_CONFIG_FPATH)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)

        self.scene = None
        self.camera = None
        self.plane = None
        self.viewport = None

        self.logger = utils_logging.get_project_logger()

    def setup(self):

        # Create basic objects required for rendering
        self.scene = Scene(name="Main Scene")
        self.camera = PerspectiveCamera(name="Main Camera", y_fov_deg=45.0)
        self.mesh = Mesh(name="Simple Mesh 1")
        self.viewport = Viewport(camera=self.camera,
                                 x=0,
                                 y=0,
                                 width=self.window_size[0],
                                 height=self.window_size[1])

        # Scene Setup
        self.scene.root_node.add(self.camera)
        self.scene.root_node.add(self.mesh)

        # DEBUG
        self.scene.root_node.print_hierarchy()

    def update(self):
        pass

    def render(self):
        self.renderer.render(scene=self.scene, viewports=[self.viewport])
        pass


def main():

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Basic Scene Demo",
        vertical_sync=True,
        enable_imgui=False
    )

    app.run()


if __name__ == "__main__":
    main()
