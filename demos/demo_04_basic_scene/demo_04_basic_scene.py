import os

from core.window import Window
from core.shader_library import ShaderLibrary
from core.renderer import Renderer
from core.scene import Scene
from core.camera import Camera
from core.mesh import Mesh
from core.light import DirectionalLight


class BasicScene(Window):

    DEMO_DIRECTORY = os.path.dirname(__file__)
    PROGRAM_CONFIG_FPATH = os.path.join(DEMO_DIRECTORY, "program_config.yaml")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create basic structures for rendering
        shader_dir = os.path.dirname(__file__)
        self.shader_library = ShaderLibrary(context=self.context, shader_directory=shader_dir)
        self.renderer = Renderer(window=self, shader_library=self.shader_library)

        self.scene = None
        self.camera = None
        self.mesh = None

    def setup(self):

        self.scene = Scene(name="Main Scene")
        self.camera = Camera(name="Main Camera")
        self.mesh = Mesh(name="Simple Mesh 1")

        # Scene Setup
        self.scene.root_node.add(self.camera)
        self.scene.root_node.add(self.mesh)

        # DEBUG
        self.scene.root_node.print_hierarchy()

    def update(self):
        pass

    def render(self):
        self.renderer.render(scene=self.scene, camera=self.camera, flags=[])
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
