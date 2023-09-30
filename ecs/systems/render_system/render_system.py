import glfw
import moderngl
from PIL import Image
import numpy as np
import struct
import logging

from ecs import constants
from ecs.systems.system import System
from ecs.component_pool import ComponentPool
from ecs.event_publisher import EventPublisher
from ecs.systems.render_system.shader_program_library import ShaderProgramLibrary
from ecs.systems.render_system.font_library import FontLibrary
from ecs.component_pool import ComponentPool
from ecs.geometry_3d import ready_to_render
from ecs.components.mesh import Mesh
from ecs.components.directional_light import DirectionalLight
from ecs.math import mat4


class RenderSystem(System):

    _type = "render_system"

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
        "entity_selection_enabled",
        "selected_entity_id",
        "shadow_map_program",
        "shadow_map_depth_texture",
        "shadow_map_framebuffer",
        "_sample_entity_location",
        "_ambient_hemisphere_light_enabled",
        "_point_lights_enabled",
        "_directional_lights_enabled",
        "_gamma_correction_enabled",
        "_shadows_enabled"
    ]

    def __init__(self,
                 logger: logging.Logger,
                 component_pool: ComponentPool,
                 event_publisher: EventPublisher,
                 **kwargs):
        super().__init__(logger=logger,
                         component_pool=component_pool,
                         event_publisher=event_publisher)

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
        self.entity_selection_enabled = True
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

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self, **kwargs):

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

        # Release any previous existing textures and/or framebuffers
        def safe_release(mgl_object):
            if mgl_object is not None:
                mgl_object.release()

        safe_release(self.forward_pass_texture_color)
        safe_release(self.forward_pass_texture_normal)
        safe_release(self.forward_pass_texture_viewpos)
        safe_release(self.forward_pass_texture_entity_info)
        safe_release(self.forward_pass_texture_depth)
        safe_release(self.forward_pass_framebuffer)
        safe_release(self.selection_pass_texture_color)
        safe_release(self.selection_pass_framebuffer)

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

        # Selection Pass
        self.selection_pass_texture_color = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.selection_pass_texture_color.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.selection_pass_texture_color.repeat_x = False  # This prevents outlining from spilling over to the other edge
        self.selection_pass_texture_color.repeat_y = False
        self.selection_pass_texture_depth = self.ctx.depth_texture(size=window_size)
        self.selection_pass_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.selection_pass_texture_color],
            depth_attachment=self.selection_pass_texture_depth)

        # Screen quads


    def on_event(self, event_type: int, event_data: tuple):

        if event_type == constants.EVENT_WINDOW_FRAMEBUFFER_SIZE:
            # TODO: Safe release all offscreen framebuffers and create new ones
            self.buffer_size = event_data
            self.create_framebuffers(window_size=self.buffer_size)

        if event_type == constants.EVENT_MOUSE_BUTTON_ENABLED:
            self.entity_selection_enabled = True

        if event_type == constants.EVENT_MOUSE_BUTTON_DISABLED:
            self.entity_selection_enabled = False

        if self.entity_selection_enabled:
            if (event_type == constants.EVENT_MOUSE_BUTTON_PRESS and
                    event_data[constants.EVENT_INDEX_MOUSE_BUTTON_BUTTON] == glfw.MOUSE_BUTTON_LEFT):

                # TODO: Move this to its own function!
                # Pass the coordinate of the pixel you want to sample to the fragment picking shader
                self.picker_program['texel_pos'].value = event_data[constants.EVENT_INDEX_MOUSE_BUTTON_X:]  # (x, y)
                self.forward_pass_texture_entity_info.use(location=0)

                self.picker_vao.transform(
                    self.picker_buffer,
                    mode=moderngl.POINTS,
                    vertices=1,
                    first=0,
                    instances=1)

                self.selected_entity_id, instance_id, _ = struct.unpack("3i", self.picker_buffer.read())

                self.event_publisher.publish(event_type=constants.EVENT_ACTION_ENTITY_SELECTED,
                                             event_data=(self.selected_entity_id,),
                                             sender=self)

        if event_type == constants.EVENT_KEYBOARD_PRESS:

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

        if event_type == constants.EVENT_ACTION_ENTITY_SELECTED:
            # Other systems may change the selected entity, so this should be reflected by the render system
            self.selected_entity_id = event_data[0]

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        # Initialise object on the GPU if they haven't been already
        camera_entity_uids = list(self.component_pool.camera_components.keys())

        # DEBUG -HACK TODO: MOVE THIS TO THE TRANSFORM SYSTEM!!!
        for _, transform in self.component_pool.transform_3d_components.items():
            transform.update()

        # Render shadow texture (if enabled)
        self.render_shadow_mapping_pass(component_pool=self.component_pool)

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:
            self.render_forward_pass(component_pool=self.component_pool,
                                     camera_uid=camera_uid)
            self.render_selection_pass(component_pool=self.component_pool,
                                       camera_uid=camera_uid,
                                       selected_entity_uid=self.selected_entity_id)
            self.render_text_2d_pass(component_pool=self.component_pool)

        # Final pass renders everything to a full screen quad from the offscreen textures
        self.render_screen_pass()

        return True

    def shutdown(self):

        # Release textures
        for texture_name, texture_obj in self.textures.items():
            texture_obj.release()

        # Release Framebuffers
        for frabuffer_name, framebuffer_obj in self.framebuffers.items():
            framebuffer_obj.release()

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

    def render_forward_pass(self, component_pool: ComponentPool, camera_uid: int):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!
        self.forward_pass_framebuffer.use()

        camera_component = component_pool.camera_components[camera_uid]
        camera_transform = component_pool.transform_3d_components[camera_uid]
        camera_component.update_viewport(window_size=self.buffer_size)

        # Clear context (you need to use the use() first to bind it!)
        self.ctx.clear(
            red=1,
            green=1,
            blue=1,
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
        program["view_matrix"].write(camera_transform.local_matrix.T.tobytes())

        camera_transform.update()
        camera_component.upload_uniforms(
            program=program,
            window_width=self.buffer_size[0],
            window_height=self.buffer_size[1])

        # Lights
        program["num_point_lights"].value = len(self.component_pool.point_light_components)
        for index, (uid, point_light_component) in enumerate(self.component_pool.point_light_components.items()):

            light_transform = self.component_pool.transform_3d_components[uid]

            program[f"point_lights[{index}].position"] = light_transform.position
            program[f"point_lights[{index}].diffuse"] = point_light_component.diffuse
            program[f"point_lights[{index}].specular"] = point_light_component.specular
            program[f"point_lights[{index}].attenuation_coeffs"] = point_light_component.attenuation_coeffs
            program[f"point_lights[{index}].enabled"] = point_light_component.enabled

        program["num_directional_lights"].value = len(self.component_pool.directional_light_components)
        for index, (uid, dir_light_component) in enumerate(self.component_pool.directional_light_components.items()):
            light_transform = self.component_pool.transform_3d_components[uid]

            program[f"directional_lights[{index}].direction"] = tuple(light_transform.local_matrix[:3, 2])
            program[f"directional_lights[{index}].diffuse"] = dir_light_component.diffuse
            program[f"directional_lights[{index}].specular"] = dir_light_component.specular
            program[f"directional_lights[{index}].strength"] = dir_light_component.strength
            program[f"directional_lights[{index}].shadow_enabled"] = dir_light_component.shadow_enabled
            program[f"directional_lights[{index}].enabled"] = dir_light_component.enabled

        # Renderables
        for uid, mesh_component in component_pool.mesh_components.items():

            if not mesh_component.visible:
                continue

            # Set entity ID
            program[constants.SHADER_UNIFORM_ENTITY_ID] = uid
            mesh_transform = component_pool.transform_3d_components[uid]

            material = component_pool.material_components.get(uid, None)

            # Upload uniforms
            program["entity_id"].value = uid
            program["model_matrix"].write(mesh_transform.local_matrix.T.tobytes())
            program["ambient_hemisphere_light_enabled"].value = self._ambient_hemisphere_light_enabled
            program["directional_lights_enabled"].value = self._directional_lights_enabled
            program["point_lights_enabled"].value = self._point_lights_enabled
            program["gamma_correction_enabled"].value = self._gamma_correction_enabled
            program["shadows_enabled"].value = self._shadows_enabled

            # TODO: Technically, you only need to upload the material once since it doesn't change.
            #       The program will keep its variable states!
            if material is not None:
                program["material.diffuse"].value = material.diffuse
                program["material.specular"].value = material.specular
                program["material.shininess_factor"] = material.shininess_factor

            # Render the vao at the end
            mesh_component.vaos[constants.SHADER_PROGRAM_FORWARD_PASS].render(moderngl.TRIANGLES)

            # Stage: Draw transparent objects back to front

    def render_selection_pass(self, component_pool: ComponentPool, camera_uid: int, selected_entity_uid: int):

        # IMPORTANT: It uses the current bound framebuffer!

        self.selection_pass_framebuffer.use()
        camera_component = component_pool.camera_components[camera_uid]
        self.ctx.clear(depth=1.0, viewport=camera_component.viewport_pixels)

        # TODO: Numbers between 0 and 1 are background colors, so we assume they are NULL selection
        if selected_entity_uid is None or selected_entity_uid <= 1:
            return

        # Safety checks before we go any further!
        renderable_transform = component_pool.transform_3d_components.get(selected_entity_uid, None)
        if renderable_transform is None:
            return

        mesh_component = component_pool.mesh_components.get(selected_entity_uid, None)
        if mesh_component is None:
            return

        camera_transform = component_pool.transform_3d_components[camera_uid]
        camera_transform.update()

        # Upload uniforms
        program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]
        camera_component.upload_uniforms(program=program,
                                         window_width=self.buffer_size[0],
                                         window_height=self.buffer_size[1])
        program["view_matrix"].write(camera_transform.local_matrix.T.tobytes())
        program["model_matrix"].write(renderable_transform.local_matrix.T.tobytes())

        # Render
        mesh_component.vaos[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS].render(moderngl.TRIANGLES)

    def render_text_2d_pass(self, component_pool: ComponentPool):

        if len(component_pool.text_2d_components) == 0:
            return

        self.forward_pass_framebuffer.use()
        self.ctx.disable(moderngl.DEPTH_TEST)

        # Upload uniforms TODO: Move this to render system
        projection_matrix = mat4.orthographic_projection(
            left=0,
            right=self.buffer_size[0],
            bottom=self.buffer_size[1],
            top=0,
            near=-1,
            far=1)

        # Upload uniforms
        program = self.shader_program_library[constants.SHADER_PROGRAM_TEXT_2D]
        program["projection_matrix"].write(projection_matrix.T.tobytes())

        # Update VBOs and render text
        for _, text_2d in component_pool.text_2d_components.items():

            # State Updates
            text_2d.initialise_on_gpu(ctx=self.ctx, shader_library=self.shader_program_library)
            text_2d.update_buffer(font_library=self.font_library)

            # Rendering
            self.textures[text_2d.font_name].use(location=0)
            text_2d.vao.render(moderngl.POINTS)

    def render_shadow_mapping_pass(self, component_pool: ComponentPool):

        self.shadow_map_framebuffer.clear()
        self.shadow_map_framebuffer.use()

        program = self.shader_program_library[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS]

        # Find which directional light, if any creates shadows
        dir_light_uid = None
        for uid, directional_light in component_pool.directional_light_components.items():
            if directional_light.shadow_enabled:
                dir_light_uid = uid
                break

        if dir_light_uid is None:
            return

        for entity_uid, mesh_component in component_pool.mesh_components.items():

            material = component_pool.material_components[entity_uid]

            # TODO: IF you forget to declare the material in the xml, you are fucked. Make sure a default material
            if not mesh_component.visible and not material.is_transparent():
                continue

            mesh_transform = component_pool.transform_3d_components[entity_uid]
            light_transform = component_pool.transform_3d_components[dir_light_uid]

            program["view_matrix"].write(light_transform.local_matrix.T.tobytes())
            program["model_matrix"].write(mesh_transform.local_matrix.T.tobytes())

            mesh_component.vaos[constants.SHADER_PROGRAM_SHADOW_MAPPING_PASS].render(moderngl.TRIANGLES)

    def render_screen_pass(self) -> None:

        """
        Renders selected offscreen texture to window. By default, it is the color texture, but you can
        change it using F1-F12 keys.
        :return: None
        """

        self.ctx.screen.use()
        self.ctx.screen.clear(red=1, green=1, blue=1)  # TODO: Check if this line is necessary
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.forward_pass_texture_color.use(location=0)
        self.forward_pass_texture_normal.use(location=1)
        self.forward_pass_texture_viewpos.use(location=2)
        self.forward_pass_texture_entity_info.use(location=3)
        self.selection_pass_texture_color.use(location=4)
        self.forward_pass_texture_depth.use(location=5)

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
