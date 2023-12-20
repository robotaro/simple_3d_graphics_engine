import moderngl

from src.core import constants
from src.core.scene import Scene
from src.math import mat4
from src.systems.render_system.render_pass import RenderPass


class RenderPassSelection(RenderPass):

    name = "selection_pass"

    __slots__ = [
        "texture_color",
        "texture_depth",
        "framebuffer"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.texture_color = None
        self.texture_depth = None
        self.framebuffer = None

    def create_framebuffers(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.texture_color = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.texture_color.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.texture_color.repeat_x = False  # This prevents outlining from spilling over to the other edge
        self.texture_color.repeat_y = False
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

        # TODO: Numbers between 0 and 1 are background colors, so we assume they are NULL selection
        if selected_entity_uid is None or selected_entity_uid <= 1:
            return

        self.framebuffer.use()

        camera_entity_uids = scene.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        for camera_uid in camera_entity_uids:

            # IMPORTANT: It uses the current bound framebuffer!
            camera_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
            camera_component = camera_pool[camera_uid]

            self.framebuffer.viewport = camera_component.viewport_pixels
            self.framebuffer.clear(depth=1.0, viewport=camera_component.viewport_pixels)

            mesh_component = scene.get_component(entity_uid=selected_entity_uid,
                                                      component_type=constants.COMPONENT_TYPE_MESH)
            if mesh_component is None:
                return

            transform_3d_pool = scene.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

            # Safety checks before we go any further!
            renderable_transform = transform_3d_pool[selected_entity_uid]
            if renderable_transform is None:
                return

            # Upload uniforms
            program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]
            camera_component.upload_uniforms(program=program)
            program["view_matrix"].write(transform_3d_pool[camera_uid].inverse_world_matrix.T.tobytes())
            program["model_matrix"].write(renderable_transform.world_matrix.T.tobytes())

            # Render
            mesh_component.vaos[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS].render(mode=mesh_component.render_mode)

    def release(self):
        self.safe_release(self.texture_color)
        self.safe_release(self.texture_depth)
        self.safe_release(self.framebuffer)
