from ecs.systems.render_system import RenderSystem

class App:

    def __init__(self):

        # Components
        self.transform_components = {}
        self.camera_components = {}
        self

        # Systems
        self.render_system = RenderSystem()

        pass