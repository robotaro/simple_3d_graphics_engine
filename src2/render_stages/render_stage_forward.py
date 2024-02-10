import moderngl

from src.core import constants
from src.core.scene import Scene
from src2.render_stages.render_stage import RenderStage


class RenderStageForward(RenderStage):

    __slots__ = [
        "texture_color",
        "texture_normal",
        "texture_viewpos",
        "texture_entity_info",
        "texture_depth",
        "framebuffer",
        "render_layers",
        "experiment_framebuffer",
        "ambient_hemisphere_light_enabled",
        "point_lights_enabled",
        "directional_lights_enabled",
        "gamma_correction_enabled",
        "shadows_enabled",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.program = self.shader_program_library[constants.SHADER_PROGRAM_FORWARD_PASS]

        # Flags
        self.ambient_hemisphere_light_enabled = True
        self.point_lights_enabled = True
        self.directional_lights_enabled = False
        self.gamma_correction_enabled = True
        self.shadows_enabled = False

        # Initialise framebuffers
        self.update_framebuffer(window_size=kwargs["initial_window_size"])

    def update_framebuffer(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.textures["color"] = self.ctx.texture(size=window_size, components=4)
        self.textures["normal"] = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.textures["viewpos"] = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.textures["entity_info"] = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.textures["entity_info"].filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.textures["depth"] = self.ctx.depth_texture(size=window_size)
        self.framebuffer = self.ctx.framebuffer(
            color_attachments=[
                self.textures["color"],
                self.textures["normal"],
                self.textures["viewpos"],
                self.textures["entity_info"]],
            depth_attachment=self.textures["depth"])

    def upload_uniforms_point_lights(self, point_lights_ubo: moderngl.Buffer):

        for index, (mesh_entity_uid, point_light_component) in enumerate(point_light_pool.items()):
            point_light_component.update_ubo(ubo=point_lights_ubo)

    def upload_uniforms_directional_lights(self, scene: Scene, program: moderngl.Program):

        directional_light_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT)
        transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM)

        program["num_directional_lights"].value = len(directional_light_pool)
        for index, (mesh_entity_uid, dir_light_component) in enumerate(directional_light_pool.items()):

            light_transform = transform_3d_pool[mesh_entity_uid]
            program[f"directional_lights[{index}].direction"] = tuple(light_transform.world_matrix[:3, 2])
            program[f"directional_lights[{index}].diffuse"] = dir_light_component.diffuse
            program[f"directional_lights[{index}].specular"] = dir_light_component.specular
            program[f"directional_lights[{index}].strength"] = dir_light_component.strength
            program[f"directional_lights[{index}].shadow_enabled"] = dir_light_component.shadow_enabled
            program[f"directional_lights[{index}].enabled"] = dir_light_component.enabled

    def render(self):

        self.framebuffer.use()

        for render_layer in self.render_layers:

            # Setup viewport
            self.framebuffer.viewport = render_layer.viewport.rect_pixels

            # Setup camera
            camera = render_layer.viewport.camera
            camera_transform = camera.components["transform"]
            self.program["projection_matrix"].write(camera.projection_matrix.T.tobytes())
            self.program["view_matrix"].write(camera_transform.inverse_world_matrix.T.tobytes())
            self.program["camera_position"].value = camera_transform.position

            self.framebuffer.clear(
                color=constants.RENDER_SYSTEM_BACKGROUND_COLOR,
                alpha=1.0,
                depth=1.0,
                viewport=render_layer.viewport.rect_pixels)

            # Prepare context flags for rendering
            self.ctx.enable_only(
                moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)  # Removing has no effect? Why?
            self.ctx.cull_face = "back"
            self.ctx.blend_func = (
                moderngl.SRC_ALPHA,
                moderngl.ONE_MINUS_SRC_ALPHA,
                moderngl.ONE,
                moderngl.ONE)

            # Set lights (if any)
            self.upload_uniforms_point_lights(scene=scene, point_lights_ubo=point_lights_ubo)
            self.upload_uniforms_directional_lights(scene=scene, program=program)

            # Render entities
            for entity_group in render_layer.entity_groups:

                if not entity_group.visible:
                    continue

                for entity in entity_group.entities:

                    if not entity.visible:
                        continue

                    self.program["model_matrix"].write(entity["transform"].world_matrix.T.tobytes())
                    self.program["entity_id"].value = entity._id

                    entity.components["material"].update_ubo(ubo=ubos["materials"])

                    self.program["instanced"] = entity.num_instances > 1
                    entity.render(vao_name=constants.SHADER_PROGRAM_FORWARD_PASS,
                                  num_instances=entity.num_instances)
