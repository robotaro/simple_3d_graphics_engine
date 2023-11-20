import glfw
import moderngl
from PIL import Image
import numpy as np
import struct
import logging

from src.core import constants
from src.systems.system import System
from src.core.event_publisher import EventPublisher
from src.core.action_publisher import ActionPublisher
from src.systems.render_system.shader_program_library import ShaderProgramLibrary
from src.systems.render_system.font_library import FontLibrary
from src.core.component_pool import ComponentPool
from src.geometry_3d import ready_to_render
from src.math import mat4


class RenderSystem(System):

    name = "render_system"

    __slots__ = [
        "ctx",
        "buffer_size",
        "shader_program_library",
        "font_library",
        "framebuffers",
        "textures",
        "vbos",
        "vaos",
        "ibos",
        "quads",
        "fullscreen_selected_texture",
        "forward_pass_texture_color",
        "forward_pass_texture_normal",
        "forward_pass_texture_viewpos",
        "forward_pass_texture_entity_info",
        "forward_pass_texture_depth",
        "forward_pass_framebuffer",
        "debug_forward_pass_framebuffer",
        "overlay_pass_texture_color",
        "overlay_pass_texture_depth",
        "overlay_pass_framebuffer",
        "selection_pass_texture_color",
        "selection_pass_texture_depth",
        "selection_pass_framebuffer",
        "picker_buffer",
        "picker_program",
        "picker_output",
        "picker_vao",
        "outline_program",
        "outline_texture",
        "outline_framebuffer",
        "hovering_ui",
        "hovering_gizmo",
        "selected_entity_id",
        "shadow_map_program",
        "shadow_map_depth_texture",
        "shadow_map_framebuffer",
        "_sample_entity_location",
        "_ambient_hemisphere_light_enabled",
        "_point_lights_enabled",
        "_directional_lights_enabled",
        "_gamma_correction_enabled",
        "_shadows_enabled",
        "event_handlers"
    ]

    def __init__(self,
                 logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 action_publisher: ActionPublisher,
                 parameters: dict,
                 **kwargs):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher,
                         action_publisher=action_publisher,
                         parameters=parameters)

        self.ctx = kwargs["context"]
        self.buffer_size = kwargs["buffer_size"]
        self.shader_program_library = ShaderProgramLibrary(context=self.ctx, logger=logger)
        self.font_library = FontLibrary(logger=logger)

        # Internal components (different from normal components)
        self.framebuffers = {}
        self.textures = {}
        self.quads = {}

        self.fullscreen_selected_texture = 0  # Color is selected by default

        # Forward Pass
        self.forward_pass_texture_color = None
        self.forward_pass_texture_normal = None
        self.forward_pass_texture_viewpos = None
        self.forward_pass_texture_entity_info = None
        self.forward_pass_texture_depth = None
        self.forward_pass_framebuffer = None

        # Debug Forward Pass
        self.debug_forward_pass_framebuffer = None

        # Overlay 3D Pass
        self.overlay_pass_texture_color = None
        self.overlay_pass_texture_depth = None
        self.overlay_pass_framebuffer = None

        # Selection Pass
        self.selection_pass_texture_color = None
        self.selection_pass_texture_depth = None
        self.selection_pass_framebuffer = None

        # Fragment Picking - altogether for now
        self.picker_buffer = None
        self.picker_program = None
        self.picker_output = None
        self.picker_vao = None

        # Outline drawing
        self.outline_program = None
        self.outline_texture = None
        self.outline_framebuffer = None

        # Entity selection variables
        self.hovering_ui = False
        self.hovering_gizmo = False
        self.selected_entity_id = -1

        # Shadow Mapping
        self.shadow_map_program = None
        self.shadow_map_depth_texture = None
        self.shadow_map_framebuffer = None

        # Flags
        self._sample_entity_location = None

        self._ambient_hemisphere_light_enabled = True
        self._point_lights_enabled = True
        self._directional_lights_enabled = True
        self._gamma_correction_enabled = True
        self._shadows_enabled = False

        self.event_handlers = {
            constants.EVENT_ENTITY_SELECTED: self.handle_event_entity_selected,
            constants.EVENT_MOUSE_ENTER_UI: self.handle_event_mouse_enter_ui,
            constants.EVENT_MOUSE_LEAVE_UI: self.handle_event_mouse_leave_ui,
            constants.EVENT_MOUSE_ENTER_GIZMO_3D: self.handle_event_mouse_enter_gizmo_3d,
            constants.EVENT_MOUSE_LEAVE_GIZMO_3D: self.handle_event_mouse_leave_gizmo_3d,
            constants.EVENT_MOUSE_BUTTON_PRESS: self.handle_event_mouse_button_press,
            constants.EVENT_KEYBOARD_PRESS: self.handle_event_keyboard_press,
            constants.EVENT_WINDOW_FRAMEBUFFER_SIZE: self.handle_event_window_framebuffer_size,
        }

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self):

        # Fragment picking
        self.picker_program = self.shader_program_library["fragment_picking"]
        self.picker_buffer = self.ctx.buffer(reserve=3 * 4)  # 3 ints
        self.picker_vao = self.ctx.vertex_array(self.picker_program, [])

        # Fonts
        for font_name, font in self.font_library.fonts.items():
            self.textures[font_name] = self.ctx.texture(size=font.texture_data.shape,
                                                        data=font.texture_data.astype('f4').tobytes(),
                                                        components=1,
                                                        dtype='f4')

        # Shadow mapping
        self.shadow_map_program = self.shader_program_library["shadow_mapping"]
        self.shadow_map_depth_texture = self.ctx.depth_texture(size=self.buffer_size)
        self.shadow_map_framebuffer = self.ctx.framebuffer(depth_attachment=self.shadow_map_depth_texture)

        # Setup fullscreen quad textures
        self.quads["fullscreen"] = ready_to_render.quad_2d(context=self.ctx,
                                                           program=self.shader_program_library["screen_quad"])

        self.create_framebuffers(window_size=self.buffer_size)
        return True

    def create_framebuffers(self, window_size: tuple):

        self._release_all_framebuffers_and_textures()

        # Forward Pass
        self.forward_pass_texture_color = self.ctx.texture(size=window_size, components=4)
        self.forward_pass_texture_normal = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.forward_pass_texture_viewpos = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.forward_pass_texture_entity_info = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.forward_pass_texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.forward_pass_texture_depth = self.ctx.depth_texture(size=window_size)
        self.forward_pass_framebuffer = self.ctx.framebuffer(
            color_attachments=[
                self.forward_pass_texture_color,
                self.forward_pass_texture_normal,
                self.forward_pass_texture_viewpos,
                self.forward_pass_texture_entity_info],
            depth_attachment=self.forward_pass_texture_depth)

        # Debug Forward Pass
        self.debug_forward_pass_framebuffer = self.ctx.framebuffer(
            color_attachments=[
                self.forward_pass_texture_color],
            depth_attachment=self.forward_pass_texture_depth)

        # Overlay 3D Pass
        self.overlay_pass_texture_color = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.overlay_pass_texture_depth = self.ctx.depth_texture(size=window_size)
        self.overlay_pass_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.overlay_pass_texture_color],
            depth_attachment=self.overlay_pass_texture_depth)

        # Selection Pass
        self.selection_pass_texture_color = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.selection_pass_texture_color.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.selection_pass_texture_color.repeat_x = False  # This prevents outlining from spilling over to the other edge
        self.selection_pass_texture_color.repeat_y = False
        self.selection_pass_texture_depth = self.ctx.depth_texture(size=window_size)
        self.selection_pass_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.selection_pass_texture_color],
            depth_attachment=self.selection_pass_texture_depth)

    def _release_all_framebuffers_and_textures(self):

        def safe_release(mgl_object):
            if mgl_object is not None:
                mgl_object.release()

        safe_release(self.forward_pass_texture_color)
        safe_release(self.forward_pass_texture_normal)
        safe_release(self.forward_pass_texture_viewpos)
        safe_release(self.forward_pass_texture_entity_info)
        safe_release(self.forward_pass_texture_depth)
        safe_release(self.forward_pass_framebuffer)

        safe_release(self.debug_forward_pass_framebuffer)

        safe_release(self.overlay_pass_texture_color)
        safe_release(self.overlay_pass_texture_depth)
        safe_release(self.overlay_pass_framebuffer)

        safe_release(self.selection_pass_texture_color)
        safe_release(self.selection_pass_texture_depth)
        safe_release(self.selection_pass_framebuffer)

    # ========================================================================
    #                             Event Handling
    # ========================================================================

    def handle_event_entity_selected(self, event_data: tuple):
        self.selected_entity_id = event_data[0]

    def handle_event_mouse_enter_ui(self, event_data: tuple):
        self.hovering_ui = True

    def handle_event_mouse_leave_ui(self, event_data: tuple):
        self.hovering_ui = False

    def handle_event_mouse_enter_gizmo_3d(self, event_data: tuple):
        self.hovering_gizmo = True

    def handle_event_mouse_leave_gizmo_3d(self, event_data: tuple):
        self.hovering_gizmo = False

    def handle_event_mouse_button_press(self, event_data: tuple):
        self.process_entity_selection(event_data=event_data)

    def handle_event_keyboard_press(self, event_data: tuple):
        self.process_keyboard_press(event_data=event_data)

    def handle_event_window_framebuffer_size(self, event_data: tuple):
        self.buffer_size = event_data
        self.create_framebuffers(window_size=self.buffer_size)

        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        for _, camera_component in camera_pool.items():
            camera_component.update_viewport(window_size=self.buffer_size)

    def process_entity_selection(self, event_data: tuple):
        if self.hovering_ui or self.hovering_gizmo:
            return

        if event_data[constants.EVENT_INDEX_MOUSE_BUTTON_BUTTON] != glfw.MOUSE_BUTTON_LEFT:
            return

        # TODO: Move this to its own function!
        # Pass the coordinate of the pixel you want to sample to the fragment picking shader
        mouse_position = (int(event_data[constants.EVENT_INDEX_MOUSE_BUTTON_X]),
                          int(event_data[constants.EVENT_INDEX_MOUSE_BUTTON_Y_OPENGL]))
        self.picker_program['texel_pos'].value = mouse_position  # (x, y)
        self.forward_pass_texture_entity_info.use(location=0)

        self.picker_vao.transform(
            self.picker_buffer,
            mode=moderngl.POINTS,
            vertices=1,
            first=0,
            instances=1)

        self.selected_entity_id, instance_id, _ = struct.unpack("3i", self.picker_buffer.read())

        if self.selected_entity_id < constants.COMPONENT_POOL_STARTING_ID_COUNTER:
            self.event_publisher.publish(event_type=constants.EVENT_ENTITY_DESELECTED,
                                         event_data=(None,),
                                         sender=self)

            # Clear all pixels that represent any selected objects
            self.selection_pass_framebuffer.use()
            self.selection_pass_framebuffer.clear(depth=1.0)
            return

        self.event_publisher.publish(event_type=constants.EVENT_ENTITY_SELECTED,
                                     event_data=(self.selected_entity_id,),
                                     sender=self)

    def process_keyboard_press(self, event_data: tuple):

        # Texture debugging modes
        key_value = event_data[constants.EVENT_INDEX_KEYBOARD_KEY]
        if glfw.KEY_F1 <= key_value <= glfw.KEY_F11:
            self.fullscreen_selected_texture = key_value - glfw.KEY_F1

        # Light debugging modes
        if glfw.KEY_1 == key_value:
            self._ambient_hemisphere_light_enabled = not self._ambient_hemisphere_light_enabled
        if glfw.KEY_2 == key_value:
            self._point_lights_enabled = not self._point_lights_enabled
        if glfw.KEY_3 == key_value:
            self._directional_lights_enabled = not self._directional_lights_enabled
        if glfw.KEY_4 == key_value:
            self._gamma_correction_enabled = not self._gamma_correction_enabled
        if glfw.KEY_5 == key_value:
            self._shadows_enabled = not self._shadows_enabled

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        # Initialise object on the GPU if they haven't been already

        # Render shadow texture (if enabled)
        #self.render_shadow_mapping_pass(component_pool=self.component_pool)

        self.render_forward_pass()
        #self.render_debug_forward_pass()
        self.render_overlay_3d_pass()
        self.render_overlay_2d_pass()
        self.render_selection_pass(selected_entity_uid=self.selected_entity_id)

        # Final pass renders everything to a full screen quad from the offscreen textures
        self.render_screen_pass()

        return True

    def shutdown(self):

        self._release_all_framebuffers_and_textures()

        for quad_name, quad in self.quads.items():
            if quad["vbo_vertices"] is not None:
                quad["vbo_vertices"].release()

            if quad["vbo_uvs"] is not None:
                quad["vbo_uvs"].release()

            if quad["vao"] is not None:
                quad["vao"].release()

        self.shader_program_library.shutdown()
        self.font_library.shutdown()

    # =========================================================================
    #                           Render Passes
    # =========================================================================

    def render_forward_pass(self):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!

        self.forward_pass_framebuffer.use()

        camera_entity_uids = self.component_pool.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
            transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

            camera_component = camera_pool[camera_uid]
            camera_transform = transform_3d_pool[camera_uid]
            self.forward_pass_framebuffer.viewport = camera_component.viewport_pixels

            # TODO: FInd out how this viewport affects the location of the rendering. Clearing seems to also set the
            #       viewport in a weird way...
            self.forward_pass_framebuffer.clear(
                color=constants.RENDER_SYSTEM_BACKGROUND_COLOR,
                alpha=1.0,
                depth=1.0,
                viewport=camera_component.viewport_pixels)

            # Prepare context flags for rendering
            self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)  # Removing has no effect? Why?
            self.ctx.cull_face = "back"
            self.ctx.blend_func = (
                moderngl.SRC_ALPHA,
                moderngl.ONE_MINUS_SRC_ALPHA,
                moderngl.ONE,
                moderngl.ONE)

            program = self.shader_program_library[constants.SHADER_PROGRAM_FORWARD_PASS]

            # Setup camera
            camera_component.upload_uniforms(program=program)
            program["view_matrix"].write(camera_transform.world_matrix.T.tobytes())

            # Setup lights
            self.upload_uniforms_point_lights(program=program)
            self.upload_uniforms_directional_lights(program=program)

            # Render meshes
            mesh_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MESH)
            transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
            material_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MATERIAL)

            for mesh_entity_uid, mesh_component in mesh_pool.items():

                if not mesh_component.visible or mesh_component.layer == constants.RENDER_SYSTEM_LAYER_OVERLAY:
                    continue

                # Mesh uniforms
                program["entity_id"].value = mesh_entity_uid
                program["model_matrix"].write(transform_3d_pool[mesh_entity_uid].world_matrix.T.tobytes())
                program["ambient_hemisphere_light_enabled"].value = self._ambient_hemisphere_light_enabled
                program["directional_lights_enabled"].value = self._directional_lights_enabled
                program["point_lights_enabled"].value = self._point_lights_enabled
                program["gamma_correction_enabled"].value = self._gamma_correction_enabled
                program["shadows_enabled"].value = self._shadows_enabled

                # TODO: Technically, you only need to upload the material once since it doesn't change.
                #       The program will keep its variable states!
                material_component = material_pool[mesh_entity_uid]
                if material_component is not None:
                    material_component.upload_uniforms(program=program)

                mesh_component.render(shader_pass_name=constants.SHADER_PROGRAM_FORWARD_PASS)

                # Stage: Draw transparent objects back to front

    def upload_uniforms_point_lights(self, program: moderngl.Program):

        point_light_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_POINT_LIGHT)
        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

        program["num_point_lights"].value = len(point_light_pool)
        for index, (mesh_entity_uid, point_light_component) in enumerate(point_light_pool.items()):
            light_transform = transform_3d_pool[mesh_entity_uid]

            program[f"point_lights[{index}].position"] = light_transform.position
            program[f"point_lights[{index}].diffuse"] = point_light_component.diffuse
            program[f"point_lights[{index}].specular"] = point_light_component.specular
            program[f"point_lights[{index}].attenuation_coeffs"] = point_light_component.attenuation_coeffs
            program[f"point_lights[{index}].enabled"] = point_light_component.enabled

    def upload_uniforms_directional_lights(self, program: moderngl.Program):

        directional_light_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT)
        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

        program["num_directional_lights"].value = len(directional_light_pool)
        for index, (mesh_entity_uid, dir_light_component) in enumerate(directional_light_pool.items()):

            light_transform = transform_3d_pool[mesh_entity_uid]
            program[f"directional_lights[{index}].direction"] = tuple(light_transform.world_matrix[:3, 2])
            program[f"directional_lights[{index}].diffuse"] = dir_light_component.diffuse
            program[f"directional_lights[{index}].specular"] = dir_light_component.specular
            program[f"directional_lights[{index}].strength"] = dir_light_component.strength
            program[f"directional_lights[{index}].shadow_enabled"] = dir_light_component.shadow_enabled
            program[f"directional_lights[{index}].enabled"] = dir_light_component.enabled

    def render_debug_forward_pass(self):

        """
        THIS FUNCTION IS BROKEN!!!!!!!!
        :return:
        """

        camera_entity_uids = self.component_pool.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        camera_component = self.component_pool.camera_components[camera_uid]
        camera_transform = self.component_pool.transform_3d_components[camera_uid]

        for debug_mesh_entity_uid, debug_mesh_component in self.component_pool.debug_mesh_components.items():

            if not debug_mesh_component.visible or debug_mesh_component.num_instances == 0:
                continue

            program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]
            camera_component.upload_uniforms(program=program)
            program["view_matrix"].write(camera_transform.world_matrix.T.tobytes())

            debug_mesh_component.render(shader_pass_name=constants.SHADER_PROGRAM_DEBUG_FORWARD_PASS)

            # Stage: Draw transparent objects back to front

    def render_overlay_3d_pass(self):

        self.overlay_pass_framebuffer.use()

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!
        camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
        transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
        mesh_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_MESH)

        # Every Render pass operates on the OFFSCREEN buffers only
        camera_entity_uids = self.component_pool.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)
        for camera_uid in camera_entity_uids:

            camera_component = camera_pool[camera_uid]
            camera_transform = transform_3d_pool[camera_uid]
            self.overlay_pass_framebuffer.viewport = camera_component.viewport_pixels

            # Clear context (you need to use the use() first to bind it!)
            self.overlay_pass_framebuffer.clear(
                color=(-1.0, -1.0, -1.0),
                alpha=1.0,
                depth=1.0,
                viewport=camera_component.viewport_pixels)

            program = self.shader_program_library[constants.SHADER_PROGRAM_OVERLAY_3D_PASS]

            # Setup camera
            camera_component.upload_uniforms(program=program)
            program["view_matrix"].write(camera_transform.world_matrix.T.tobytes())

            # Render meshes
            for mesh_entity_uid, mesh_component in mesh_pool.items():

                if (not mesh_component.visible or
                        mesh_component.layer != constants.RENDER_SYSTEM_LAYER_OVERLAY or
                        mesh_component.exclusive_to_camera_uid != camera_uid):
                    continue

                mesh_transform = self.component_pool.get_component(entity_uid=mesh_entity_uid,
                                                                   component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

                material = self.component_pool.get_component(entity_uid=mesh_entity_uid,
                                                             component_type=constants.COMPONENT_TYPE_MATERIAL)

                # Upload uniforms
                program["model_matrix"].write(mesh_transform.world_matrix.T.tobytes())

                # TODO: Technically, you only need to upload the material once since it doesn't change.
                #       The program will keep its variable states!
                if material is not None:
                    program["color_diffuse"].value = material.diffuse_highlight if material.state_highlighted else material.diffuse

                # Render the mesh
                mesh_component.vaos[constants.SHADER_PROGRAM_OVERLAY_3D_PASS].render(mode=mesh_component.render_mode)

    def render_overlay_2d_pass(self):

        self.overlay_pass_framebuffer.use()
        # Note: There is no framebuffer.clear() because it is done on the 3D pass. This may change in the future

        camera_entity_uids = self.component_pool.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            overlay_2d_component = self.component_pool.get_component(entity_uid=camera_uid,
                                                                     component_type=constants.COMPONENT_TYPE_OVERLAY_2D)

            if overlay_2d_component is None:
                return

            # ============== [ DEBUG ] ========================
            #overlay_2d_component.im_overlay.add_aabb_filled(50., 50., 100., 100., (0., 0., 0., 1.0))
            #overlay_2d_component.im_overlay.add_text("this is a test, this is a test, this is a test, this is a test, this is a test, ", 50., 50.)
            #overlay_2d_component.im_overlay.add_circle_edge(100., 100., 25., 4., (1., 0., 1., 1.0))

            if overlay_2d_component.im_overlay.num_draw_commands == 0:
                return

            camera_component = self.component_pool.get_component(entity_uid=camera_uid,
                                                                 component_type=constants.COMPONENT_TYPE_CAMERA)

            self.overlay_pass_framebuffer.viewport = camera_component.viewport_pixels
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

    def render_selection_pass(self, selected_entity_uid: int):

        # TODO: Numbers between 0 and 1 are background colors, so we assume they are NULL selection
        if selected_entity_uid is None or selected_entity_uid <= 1:
            return

        self.selection_pass_framebuffer.use()

        camera_entity_uids = self.component_pool.get_all_entity_uids(component_type=constants.COMPONENT_TYPE_CAMERA)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            # IMPORTANT: It uses the current bound framebuffer!
            camera_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
            camera_component = camera_pool[camera_uid]

            self.selection_pass_framebuffer.viewport = camera_component.viewport_pixels
            self.selection_pass_framebuffer.clear(depth=1.0, viewport=camera_component.viewport_pixels)

            mesh_component = self.component_pool.get_component(entity_uid=selected_entity_uid,
                                                               component_type=constants.COMPONENT_TYPE_MESH)
            if mesh_component is None:
                return

            transform_3d_pool = self.component_pool.get_pool(component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

            # Safety checks before we go any further!
            renderable_transform = transform_3d_pool[selected_entity_uid]
            if renderable_transform is None:
                return

            # Upload uniforms
            program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]
            camera_component.upload_uniforms(program=program)
            program["view_matrix"].write(transform_3d_pool[camera_uid].world_matrix.T.tobytes())
            program["model_matrix"].write(renderable_transform.world_matrix.T.tobytes())

            # Render
            mesh_component.vaos[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS].render(mode=mesh_component.render_mode)


    def render_shadow_mapping_pass(self, component_pool: ComponentPool):

        # TODO: This function's code is old and won't probably work!

        self.shadow_map_framebuffer.clear()
        self.shadow_map_framebuffer.use()

        program = self.shader_program_library[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS]

        # Find which directional light, if any creates shadows
        directional_light_uid = None
        for uid, directional_light in component_pool.directional_light_components.items():
            if directional_light.shadow_enabled:
                directional_light_uid = uid
                break

        if directional_light_uid is None:
            return

        for mesh_entity_uid, mesh_component in component_pool.mesh_components.items():

            material = component_pool.material_components[mesh_entity_uid]

            # TODO: IF you forget to declare the material in the xml, you are fucked. Make sure a default material
            if not mesh_component.visible and not material.is_transparent():
                continue

            mesh_transform = component_pool.get_component(entity_uid=mesh_entity_uid,
                                                          component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
            light_transform = component_pool.get_component(entity_uid=directional_light_uid,
                                                           component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)

            program["view_matrix"].write(light_transform.world_matrix.T.tobytes())
            program["model_matrix"].write(mesh_transform.world_matrix.T.tobytes())

            mesh_component.vaos[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS].render(mesh_component.render_mode)

    def render_screen_pass(self) -> None:

        """
        Renders selected offscreen texture to window. By default, it is the color texture, but you can
        change it using F1-F12 keys.
        :return: None
        """

        self.ctx.screen.use()
        self.ctx.screen.clear()

        self.forward_pass_texture_color.use(location=0)
        self.forward_pass_texture_normal.use(location=1)
        self.forward_pass_texture_viewpos.use(location=2)
        self.forward_pass_texture_entity_info.use(location=3)
        self.selection_pass_texture_color.use(location=4)
        self.overlay_pass_texture_color.use(location=5)
        self.forward_pass_texture_depth.use(location=6)

        quad_vao = self.quads["fullscreen"]['vao']
        quad_vao.program["selected_texture"] = self.fullscreen_selected_texture
        quad_vao.render(moderngl.TRIANGLES)

    # =========================================================================
    #                         Other Functions
    # =========================================================================

    def load_texture_from_file(self, texture_fpath: str, texture_id: str, datatype="f4"):
        if texture_id in self.textures:
            raise KeyError(f"[ERROR] Texture ID '{texture_id}' already exists")

        image = Image.open(texture_fpath)
        image_data = np.array(image)
        self.textures[texture_id] = self.ctx.texture(size=image.size,
                                                     components=image_data.shape[-1],
                                                     data=image_data.tobytes())
