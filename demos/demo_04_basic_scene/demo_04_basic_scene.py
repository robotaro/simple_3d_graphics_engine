import os
import logging

from core import constants
from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer
from core.scene import Scene
from core.camera import PerspectiveCamera
from core.viewport import Viewport
from core.mesh import Mesh
from core.material import Material
from core.utilities import utils_logging
from core.geometry_3d.mesh_loader import MeshFactory


class BasicScene(Window):

    DEMO_DIRECTORY = os.path.dirname(__file__)
    PROGRAM_CONFIG_FPATH = os.path.join(DEMO_DIRECTORY, "programs.yaml")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create basic structures for rendering
        self.shader_library = ShaderLibrary(context=self.context,
                                            shader_programs_config_fpath=BasicScene.PROGRAM_CONFIG_FPATH)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)

        self.scene = None
        self.camera = None
        self.mesh = None
        self.material = None
        self.viewport = None

        self.logger = utils_logging.get_project_logger()

    def setup(self):

        # Create basic objects required for rendering
        self.scene = Scene(name="Main Scene")
        self.camera = PerspectiveCamera(name="Main Camera",
                                        y_fov_deg=45.0,
                                        translation=(0, 0, -3))
        self.material = Material()

        self.viewport = Viewport(camera=self.camera,
                                 x=0, y=0,
                                 width=self.window_size[0],
                                 height=self.window_size[1])

        # Load mesh data
        loader = MeshFactory()
        mesh_fpath = os.path.join(constants.RESOURCES_DIR, "models", "dragon.obj")
        self.mesh = loader.from_obj(name="Dragon", program_name="simple_mesh", fpath=mesh_fpath)

        # Scene Setup
        self.scene.root_node.add(self.camera)
        self.scene.root_node.add(self.mesh)

        # DEBUG
        self.scene.root_node.print_hierarchy()

    def update(self, delta_time: float):
        #print("[DEMO 04] update")
        pass

    def render(self):
        #print("[DEMO 04] render")
        self.renderer.render(scene=self.scene, viewports=[self.viewport])


def main():

    app = BasicScene(
        window_size=(1024, 768),
        window_title="Basic Scene Demo",
        vertical_sync=True,
        imgui_enabled=False
    )

    app.run()


if __name__ == "__main__":
    main()
