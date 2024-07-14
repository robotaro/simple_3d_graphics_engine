from src3 import constants

from src3.entities.entity import Entity


class BezierCurveEntity(Entity):

    def __init__(self,
                 render_mode=constants.MESH_RENDER_MODE_TRIANGLES,
                 lighting_mode=constants.MESH_LIGHTING_MODE_LIT,
                 **kwargs):

        super().__init__(**kwargs)
        self.lighting_mode = lighting_mode
        self.render_mode = render_mode

        # TODO: Consider between using one program for solid lighting or one for everything
        self.program = self.shader_loader.get_program(shader_filename="basic.glsl")

    def render(self, entity_id=None):

        self.ubo_manager.update_ubo(
            ubo_id="mvp",
            variable_id="m_model",
            data=self.component_transform.world_matrix)

        if entity_id:
            self.program["entity_id"].value = entity_id

        self.component_mesh.vao.render(mode=self.render_mode, instances=1)
