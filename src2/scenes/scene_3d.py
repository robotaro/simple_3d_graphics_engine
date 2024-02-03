from src2.scenes.scene import Scene

from src2.render_stages.render_stage_forward import RenderStageForward
from src2.render_stages.render_stage_selection import RenderStageSelection
from src2.render_stages.render_stage_overlay import RenderStageOverlay
from src2.render_stages.render_stage_shadow import RenderStageShadow
from src2.render_stages.render_stage_screen import RenderStageScreen


class Scene3D(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        render_stage_forward = RenderStageForward(
            ctx=self.ctx,
            shader_library=self.shader_library)
        self.render_stages.append(render_stage_forward)

        render_stage_selection = RenderStageSelection(
            ctx=self.ctx,
            shader_library=self.shader_library)
        self.render_stages.append(render_stage_selection)

        render_stage_overlay = RenderStageOverlay(
            ctx=self.ctx,
            shader_library=self.shader_library)
        self.render_stages.append(render_stage_overlay)

        render_stage_screen = RenderStageScreen(
            ctx=self.ctx,
            shader_library=self.shader_library,
            textures={
                "forward/color": render_stage_forward.textures["color"],
                "forward/normal": render_stage_forward.textures["normal"],
                "forward/viewpos": render_stage_forward.textures["viewpos"],
                "forward/entity_info": render_stage_forward.textures["entity_info"],
                "selection/color": render_stage_selection.textures["color"],
                "overlay/color": render_stage_overlay.textures["color"],
                "forward/depth": render_stage_forward.textures["depth"]})
        self.render_stages.append(render_stage_screen)

    def render(self):
        for render_stage in self.render_stages:
            render_stage.render()

    def update