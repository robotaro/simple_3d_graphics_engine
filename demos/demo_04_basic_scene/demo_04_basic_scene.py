import os
import time
import logging

import numpy as np

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
from core.math import mat4


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
        self.dir_light = None
        self.mesh = None
        self.material = None
        self.viewport = None

        self.logger = utils_logging.get_project_logger()

    def setup(self):

        # Create basic objects required for rendering
        self.scene = Scene(name="Main Scene")
        self.camera = self.scene.create_perspective_camera(name="Main Camera",
                                                           position=(0, 0, -2))
        self.material = Material()

        self.viewport = Viewport(camera=self.camera,
                                 x=0, y=0,
                                 width=self.window_size[0],
                                 height=self.window_size[1])

        # Load mesh data
        loader = MeshFactory()
        mesh_fpath = os.path.join(constants.RESOURCES_DIR, "models", "dragon.obj")
        self.mesh = loader.from_obj(name="Dragon", program_name="mesh_with_lights", fpath=mesh_fpath)

        # Scene Setup
        self.scene._root_node.add(self.camera)
        self.scene._root_node.add(self.mesh)

        # DEBUG
        self.scene._root_node.print_hierarchy()
        self.renderer.load_texture_from_file(texture_fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\demos\demo_04_basic_scene\ball.png",
                                             texture_id="ball",
                                             datatype="u8")

        self.renderer.initialize()

    def update(self, delta_time: float):
        self.mesh.transform = mat4.compute_transform(position=(0, 0, 0),
                                                     rotation_rad=(0, time.perf_counter(), 0))

    def render(self):
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
