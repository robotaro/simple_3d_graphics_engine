import moderngl

from src.core import constants
from src.core.scene import Scene
from src.math import mat4
from src.systems.render_system.render_pass import RenderPass


class RenderPassShadow(RenderPass):

    name = "shadow_pass"

    __slots__ = [
        "program",
        "depth_texture",
        "framebuffer"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.program = None
        self.depth_texture = None
        self.framebuffer = None

    def create_framebuffers(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.program = self.shader_program_library["shadow_mapping"]
        self.depth_texture = self.ctx.depth_texture(size=window_size)
        self.framebuffer = self.ctx.framebuffer(depth_attachment=self.depth_texture)

    def render(self,
               scene: Scene,
               materials_ubo: moderngl.Buffer,
               point_lights_ubo: moderngl.Buffer,
               transforms_ubo: moderngl.Buffer,
               selected_entity_uid: int):

        # TODO: This function's code is old and won't probably work!

        self.framebuffer.clear()
        self.framebuffer.use()

        program = self.shader_program_library[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS]

        # Find which directional light, if any creates shadows
        directional_light_uid = None
        for uid, directional_light in scene.directional_light_components.items():
            if directional_light.shadow_enabled:
                directional_light_uid = uid
                break

        if directional_light_uid is None:
            return

        for mesh_entity_uid, mesh_component in scene.mesh_components.items():

            material = scene.material_components[mesh_entity_uid]

            # TODO: IF you forget to declare the material in the xml, you are fucked. Make sure a default material
            if not mesh_component.visible and not material.is_transparent():
                continue

            mesh_transform = scene.get_component(entity_uid=mesh_entity_uid,
                                                 component_type=constants.COMPONENT_TYPE_TRANSFORM)
            light_transform = scene.get_component(entity_uid=directional_light_uid,
                                                  component_type=constants.COMPONENT_TYPE_TRANSFORM)

            program["view_matrix"].write(light_transform.inverse_world_matrix.T.tobytes())
            program["model_matrix"].write(mesh_transform.world_matrix.T.tobytes())

            mesh_component.vaos[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS].render(mesh_component.render_mode)

    def release(self):
        self.safe_release(self.depth_texture)
        self.safe_release(self.framebuffer)
