import moderngl
from glm import vec3, inverse

from src3 import constants

from src3.entities.entity import Entity


class PointCloudEntity(Entity):
    def __init__(self,
                 render_mode=constants.MESH_RENDER_MODE_TRIANGLES,
                 lighting_mode=constants.MESH_LIGHTING_MODE_LIT,
                 **kwargs):

        super().__init__(**kwargs)
        self.render_mode = render_mode

        self.program = self.shader_loader.get_program("points.glsl")

    def update_points(self):

        pass

    def render(self, entity_id=None):

        self.ctx.enable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = 'auto'

        self.component_point_cloud.vao.render(mode=moderngl.POINTS)

        self.ctx.disable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = None


