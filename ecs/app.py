from ecs.systems.render_system import RenderSystem



class App:

    def __init__(self):

        # Components
        self.transform_components = {}
        self.camera_components = {}
        self.vao_outline_pass_components = {}
        self.vao_forward_pass = {}
        self.vao_forward_pass = {}
        self.vao_forward_pass = {}

        # Systems
        self.render_system = RenderSystem()

        pass