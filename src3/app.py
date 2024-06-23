import imgui

from src3 import constants
from src3.shader_loader import ShaderLoader
from src3.window_glfw import WindowGLFW
from src.utilities import utils_logging

# Temporary
from src3.editors.viewer_3d import Viewer3D
from src3.editors.gltf_load_demo import GLTFLoadDemo


class App(WindowGLFW):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = utils_logging.get_project_logger(project_logger_name="Editor")
        self.shader_loader = ShaderLoader(logger=self.logger, ctx=self.ctx)

        # Temporary
        self.editors = []

    def initialise(self):
        self.shader_loader.load_shaders(directory=constants.SHADERS_DIR)

        editor_classes = [
            Viewer3D
        ]

        for editor_class in editor_classes:
            self.editors.append(editor_class(
                ctx=self.ctx,
                logger=self.logger,
                event_publisher=self.event_publisher,
                shader_loader=self.shader_loader,
                params={}
                )
            )

        # Initialise all editors and Subscribe them to all events
        for editor in self.editors:
            editor.setup()
            self.event_publisher.subscribe(listener=editor)

    def update(self, time: float, elapsed_time: float):

        for editor in self.editors:
            editor.update(time, elapsed_time=elapsed_time)

        # DEBUG
        #imgui.show_test_window()

    def shutdown(self):
        for editor in self.editors:
            self.event_publisher.unsubscribe(listener=editor)
            editor.shutdown()
