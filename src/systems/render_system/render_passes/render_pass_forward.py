import moderngl
import numpy as np

from src.core import constants
from src.core.scene import Scene
from src.systems.render_system.render_pass import RenderPass


class RenderPassForward(RenderPass):

    name = "forward_pass"

    __slots__ = [
        "texture_color",
        "texture_normal",
        "texture_viewpos",
        "texture_entity_info",
        "texture_depth",
        "framebuffer",
        "experiment_framebuffer",
        "ambient_hemisphere_light_enabled",
        "point_lights_enabled",
        "directional_lights_enabled",
        "gamma_correction_enabled",
        "shadows_enabled",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.texture_color = None
        self.texture_normal = None
        self.texture_viewpos = None
        self.texture_entity_info = None
        self.texture_depth = None
        self.framebuffer = None

        # Flags
        self.ambient_hemisphere_light_enabled = True
        self.point_lights_enabled = True
        self.directional_lights_enabled = False
        self.gamma_correction_enabled = True
        self.shadows_enabled = False

    def create_framebuffers(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.texture_color = self.ctx.texture(size=window_size, components=4)
        self.texture_normal = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.texture_viewpos = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.texture_entity_info = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.texture_depth = self.ctx.depth_texture(size=window_size)
        self.framebuffer = self.ctx.framebuffer(
            color_attachments=[
                self.texture_color,
                self.texture_normal,
                self.texture_viewpos,
                self.texture_entity_info],
            depth_attachment=self.texture_depth)

    def render(self,
               scene: Scene,
               materials_ubo: moderngl.Buffer,
               point_lights_ubo: moderngl.Buffer,
               transforms_ubo: moderngl.Buffer,
               selected_entity_uid: int):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!

        self.framebuffer.use()

        camera_entity_uids = scene.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        program = self.shader_program_library[constants.SHADER_PROGRAM_FORWARD_PASS]

        program["ambient_hemisphere_light_enabled"].value = self.ambient_hemisphere_light_enabled
        program["directional_lights_enabled"].value = self.directional_lights_enabled
        program["point_lights_enabled"].value = self.point_lights_enabled
        program["gamma_correction_enabled"].value = self.gamma_correction_enabled
        program["shadows_enabled"].value = self.shadows_enabled

        camera_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        mesh_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_MESH)
        transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
        multi_transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_MULTI_TRANSFORM_3D)
        material_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            camera_component = camera_pool[camera_uid]
            camera_transform = transform_3d_pool[camera_uid]
            self.framebuffer.viewport = camera_component.viewport_pixels

            # TODO: FInd out how this viewport affects the location of the rendering. Clearing seems to also set the
            #       viewport in a weird way...
            self.framebuffer.clear(
                color=constants.RENDER_SYSTEM_BACKGROUND_COLOR,
                alpha=1.0,
                depth=1.0,
                viewport=camera_component.viewport_pixels)

            # Prepare context flags for rendering
            self.ctx.enable_only(
                moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)  # Removing has no effect? Why?
            self.ctx.cull_face = "back"
            self.ctx.blend_func = (
                moderngl.SRC_ALPHA,
                moderngl.ONE_MINUS_SRC_ALPHA,
                moderngl.ONE,
                moderngl.ONE)

            # Setup camera
            program["projection_matrix"].write(camera_component.get_projection_matrix().T.tobytes())
            program["view_matrix"].write(camera_transform.inverse_world_matrix.T.tobytes())
            program["camera_position"].value = camera_transform.position

            # Setup lights
            self.upload_uniforms_point_lights(scene=scene, point_lights_ubo=point_lights_ubo)
            self.upload_uniforms_directional_lights(scene=scene, program=program)

            for mesh_entity_uid, mesh_component in mesh_pool.items():

                if not mesh_component.visible or mesh_component.layer == constants.RENDER_SYSTEM_LAYER_OVERLAY:
                    continue

                # Update Transform UBO
                num_instances = 1
                transform = transform_3d_pool.get(mesh_entity_uid, None)
                if transform is not None:
                    program["model_matrix"].write(transform.world_matrix.T.tobytes())

                multi_transform = multi_transform_3d_pool.get(mesh_entity_uid, None)
                if multi_transform is not None:
                    multi_transform.upload_world_matrix_to_ubo(ubo=transforms_ubo)
                    num_instances = multi_transform.world_matrices.shape[0]

                # Update Mesh uniforms
                program["entity_id"].value = mesh_entity_uid

                material_component = material_pool[mesh_entity_uid]
                if material_component is not None:
                    program["material_index"].value = material_component.ubo_index
                    material_component.update_ubo(ubo=materials_ubo)

                program["instanced"] = num_instances > 1
                mesh_component.render(shader_pass_name=constants.SHADER_PROGRAM_FORWARD_PASS,
                                      num_instances=num_instances)

                # Stage: Draw transparent objects back to front

    def upload_uniforms_point_lights(self, scene: Scene, point_lights_ubo: moderngl.Buffer):

        # TODO: Revise this and only upload what is necessary

        point_light_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_POINT_LIGHT)

        for index, (mesh_entity_uid, point_light_component) in enumerate(point_light_pool.items()):
            point_light_component.update_ubo(ubo=point_lights_ubo)

    def upload_uniforms_directional_lights(self, scene: Scene, program: moderngl.Program):

        directional_light_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT)
        transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

        program["num_directional_lights"].value = len(directional_light_pool)
        for index, (mesh_entity_uid, dir_light_component) in enumerate(directional_light_pool.items()):

            light_transform = transform_3d_pool[mesh_entity_uid]
            program[f"directional_lights[{index}].direction"] = tuple(light_transform.world_matrix[:3, 2])
            program[f"directional_lights[{index}].diffuse"] = dir_light_component.diffuse
            program[f"directional_lights[{index}].specular"] = dir_light_component.specular
            program[f"directional_lights[{index}].strength"] = dir_light_component.strength
            program[f"directional_lights[{index}].shadow_enabled"] = dir_light_component.shadow_enabled
            program[f"directional_lights[{index}].enabled"] = dir_light_component.enabled

    def release(self):
        self.safe_release(self.texture_color)
        self.safe_release(self.texture_normal)
        self.safe_release(self.texture_viewpos)
        self.safe_release(self.texture_entity_info)
        self.safe_release(self.texture_depth)
        self.safe_release(self.framebuffer)
