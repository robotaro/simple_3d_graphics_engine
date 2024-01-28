from src2.scenes.scene import Scene


class Scene3D(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create rendering pipeline
        forward_stage = self.create_render_stage(
            name="forward",
            stage_type="forward")

        g = 0

    def render(self):
        pass