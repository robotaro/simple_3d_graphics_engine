import moderngl

from src.core import constants
from src.core.scene import Scene
from src.math import mat4
from src.systems.render_system.render_pass import RenderPass


class RenderStageOverlay(RenderPass):

    name = "overlay_pass"

    __slots__ = [
        "texture_color",
        "texture_depth",
        "framebuffer"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Forward Pass
        self.texture_color = None
        self.texture_depth = None
        self.framebuffer = None

    def create_framebuffers(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.texture_color = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.texture_depth = self.ctx.depth_texture(size=window_size)
        self.framebuffer = self.ctx.framebuffer(
            color_attachments=[self.texture_color],
            depth_attachment=self.texture_depth)

    def render(self,
               scene: Scene,
               materials_ubo: moderngl.Buffer,
               point_lights_ubo: moderngl.Buffer,
               transforms_ubo: moderngl.Buffer,
               selected_entity_uid: int):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!

        self.framebuffer.use()
        self.render_3d_elements(scene=scene)
        self.render_2d_elements(scene=scene)

    def render_3d_elements(self, scene: Scene):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!
        camera_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM)
        mesh_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_MESH)
        material_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)

        # Every Render pass operates on the OFFSCREEN buffers only
        camera_entity_uids = scene.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)
        for camera_uid in camera_entity_uids:

            camera_component = camera_pool[camera_uid]
            camera_transform = transform_3d_pool[camera_uid]
            self.framebuffer.viewport = camera_component.viewport_pixels

            # Clear context (you need to use the use() first to bind it!)
            self.framebuffer.clear(
                color=(-1.0, -1.0, -1.0),
                alpha=1.0,
                depth=1.0,
                viewport=camera_component.viewport_pixels)

            program = self.shader_program_library[constants.SHADER_PROGRAM_OVERLAY_3D_PASS]

            # Setup camera
            program["projection_matrix"].write(camera_component.get_projection_matrix().T.tobytes())
            program["view_matrix"].write(camera_transform.inverse_world_matrix.T.tobytes())

            # Render meshes
            for mesh_entity_uid, mesh_component in mesh_pool.items():

                if (not mesh_component.visible or
                        mesh_component.layer != constants.RENDER_SYSTEM_LAYER_OVERLAY or
                        mesh_component.exclusive_to_camera_uid != camera_uid):
                    continue

                mesh_transform = transform_3d_pool.get(mesh_entity_uid, None)
                program["model_matrix"].write(mesh_transform.world_matrix.T.tobytes())

                material = material_pool.get(mesh_entity_uid, None)
                if material is not None:
                    program["color_diffuse"].value = material.ubo_data["diffuse_highlight"].flatten() \
                        if material.state_highlighted else material.ubo_data["diffuse"].flatten()

                # Render the mesh
                mesh_component.vaos[constants.SHADER_PROGRAM_OVERLAY_3D_PASS].render(mode=mesh_component.render_mode)

    def render_2d_elements(self, scene: Scene):
        self.framebuffer.use()
        # Note: There is no framebuffer.clear() because it is done on the 3D pass. This may change in the future

        camera_entity_uids = scene.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            overlay_2d_component = scene.get_component(entity_uid=camera_uid,
                                                       component_type=constants.COMPONENT_TYPE_OVERLAY_2D)

            if overlay_2d_component is None:
                return

            # ============== [ DEBUG ] ========================
            #overlay_2d_component.im_overlay.add_line_segments(self.debug_points_a, self.debug_points_b, self.debug_colors, 2.0)
            # overlay_2d_component.im_overlay.add_aabb_filled(50., 50., 100., 100., (0., 0., 0., 1.0))
            # overlay_2d_component.im_overlay.add_text("this is a test, this is a test, this is a test, this is a test, this is a test, ", 50., 50.)
            # overlay_2d_component.im_overlay.add_circle_edge(100., 100., 25., 4., (1., 0., 1., 1.0))

            if overlay_2d_component.im_overlay.num_draw_commands == 0:
                return

            camera_component = scene.get_component(entity_uid=camera_uid,
                                                        component_type=constants.COMPONENT_TYPE_CAMERA)

            self.framebuffer.viewport = camera_component.viewport_pixels
            self.ctx.disable(moderngl.DEPTH_TEST)

            # Upload uniforms TODO: Move this to render system
            overlay_projection_matrix = mat4.orthographic_projection(
                left=0,
                top=0,
                right=camera_component.viewport_pixels[2],
                bottom=camera_component.viewport_pixels[3],
                near=-1,
                far=1)

            # Upload uniforms
            program = self.shader_program_library[constants.SHADER_PROGRAM_OVERLAY_2D_PASS]
            program["projection_matrix"].write(overlay_projection_matrix.T.tobytes())

            # Upload VBOs
            overlay_2d_component.update_buffer()

            # Render
            self.textures[overlay_2d_component.font_name].use(location=0)
            overlay_2d_component.vao.render(mode=moderngl.POINTS)

            # And don#t forget to clear the buffer for the next frame of commands
            overlay_2d_component.im_overlay.clear()

    def release(self):
        self.safe_release(self.texture_color)
        self.safe_release(self.texture_depth)
        self.safe_release(self.framebuffer)
