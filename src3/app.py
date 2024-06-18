import imgui

from src3 import constants
from src3.shader_loader import ShaderLoader
from src3.window_glfw import WindowGLFW
from src.utilities import utils_logging

# Temporary
from src3.editors.editor_3d_viewer import Editor3DViewer
from src3.editors.video_annotator import VideoAnnotator
from src3.editors.cube_demo import CubeDemo


class App(WindowGLFW):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = utils_logging.get_project_logger(project_logger_name="Editor")
        self.shader_loader = ShaderLoader(logger=self.logger, ctx=self.ctx)

        # Temporary
        self.editors = []

    def initialise(self):
        self.shader_loader.load_shaders(directory=constants.SHADERS_DIR)

        # Create editors (temporary!)
        self.editors.append(Editor3DViewer(
            ctx=self.ctx,
            logger=self.logger,
            event_publisher=self.event_publisher,
            shader_loader=self.shader_loader,
            params={}
            )
        )

        self.editors.append(VideoAnnotator(
            ctx=self.ctx,
            logger=self.logger,
            event_publisher=self.event_publisher,
            shader_loader=self.shader_loader,
            params={})
        )

        self.editors.append(CubeDemo(
            ctx=self.ctx,
            logger=self.logger,
            event_publisher=self.event_publisher,
            shader_loader=self.shader_loader,
            params={})
        )

        # Subscribe all editors to all events
        for editor in self.editors:
            editor.initialise()
            self.event_publisher.subscribe(listener=editor)

    def update(self, elapsed_time: float):

        for editor in self.editors:
            editor.update(elapsed_time=elapsed_time)

        # DEBUG
        imgui.show_test_window()

    def shutdown(self):
        for editor in self.editors:
            self.event_publisher.unsubscribe(listener=editor)
            editor.shutdown()
