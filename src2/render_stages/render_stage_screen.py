import moderngl

from src.core import constants
from src.core.scene import Scene
from src.math import mat4
from src.geometry_3d import ready_to_render
from src2.render_stages.render_stage import RenderStage


class RenderStageScreen(RenderStage):

    __slots__ = [
        "fullscreen_quad",
        "texture_location_order"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        program = self.shader_program_library["screen_quad"]
        self.fullscreen_quad = ready_to_render.quad_2d(ctx=self.ctx, program=program)
        self.texture_location_order = [
            "forward/color",
            "forward/normal",
            "forward/viewpos",
            "forward/entity_info",
            "selection/color",
            "overlay/color",
            "forward/depth"
        ]

    def update_framebuffer(self, window_size: tuple):
        pass

    def render(self):
      
        self.ctx.screen.use()
        self.ctx.screen.clear()

        for location_index, texture_name in enumerate(self.texture_location_order):
            self.textures[texture_name].use(location=location_index)

        quad_vao = self.fullscreen_quad['vao']
        quad_vao.program["selected_texture"] = 0 # self.fullscreen_selected_texture (Value representing selected texture)
        quad_vao.render(moderngl.TRIANGLES)
