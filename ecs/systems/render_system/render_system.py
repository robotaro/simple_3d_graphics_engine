import glfw
import moderngl
from PIL import Image
import numpy as np
import struct

from ecs import constants
from ecs.systems.system import System
from ecs.systems.render_system.shader_program_library import ShaderProgramLibrary
from ecs.systems.render_system.font_library import FontLibrary
from ecs.component_pool import ComponentPool
from ecs.geometry_3d import ready_to_render
from ecs.math import mat4


class RenderSystem(System):

    _type = "render_system"

    def __init__(self, **kwargs):
        super().__init__(logger=kwargs["logger"])

        self.ctx = kwargs["context"]
        self.buffer_size = kwargs["buffer_size"]
        self.shader_program_library = ShaderProgramLibrary(context=self.ctx, logger=kwargs["logger"])
        self.font_library = FontLibrary(logger=kwargs["logger"])

        # Internal components (different from normal components)
        self.framebuffers = {}
        self.textures_offscreen_rendering = {}
        self.textures_font = {}
        self.samplers = {}
        self.vbo_groups = {}
        self.quads = {}

        self.fullscreen_selected_texture = 0  # Color is selected by default

        # Fragment Picking - altogether for now
        self.picker_buffer = None
        self.picker_program = None
        self.picker_output = None
        self.picker_vao = None

        # Outline drawing
        self.outline_program = None
        self.outline_texture = None
        self.outline_framebuffer = None

        self.selected_entity_id = None

        # Programs
        self.shadow_map_program = None

        # Flags
        self._sample_entity_location = None

    # =========================================================================
    #                         System Core functions
    # =========================================================================

    def initialise(self, **kwargs):

        # Fragment picking
        self.picker_program = self.shader_program_library["fragment_picking"]
        self.picker_program["entity_info_texture"].value = 0  # Read from texture channel 0
        self.picker_buffer = self.ctx.buffer(reserve=3 * 4)  # 3 ints
        self.picker_vao = self.ctx.vertex_array(self.picker_program, [])

        # Outline rendering
        #self.outline_program = self.shader_library["outline_pass"]
        #self.outline_program["outline_color"].value = 0

        # Offscreen rendering
        self.textures_offscreen_rendering["color"] = self.ctx.texture(size=self.buffer_size, components=4)
        self.textures_offscreen_rendering["normal"] = self.ctx.texture(size=self.buffer_size, components=4, dtype='f4')
        self.textures_offscreen_rendering["viewpos"] = self.ctx.texture(size=self.buffer_size, components=4, dtype='f4')
        self.textures_offscreen_rendering["entity_info"] = self.ctx.texture(size=self.buffer_size, components=4, dtype='f4')
        self.textures_offscreen_rendering["entity_info"].filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.textures_offscreen_rendering["depth"] = self.ctx.depth_texture(size=self.buffer_size)
        self.framebuffers["offscreen"] = self.ctx.framebuffer(
            color_attachments=[
                self.textures_offscreen_rendering["color"],
                self.textures_offscreen_rendering["normal"],
                self.textures_offscreen_rendering["viewpos"],
                self.textures_offscreen_rendering["entity_info"]
            ],
            depth_attachment=self.textures_offscreen_rendering["depth"],
        )

        # Fonts
        for font_name, font in self.font_library.fonts.items():
            self.textures_font[font_name] = self.ctx.texture(size=font.texture_data.shape, components=1, dtype='f4')

        # Selection Pass
        self.textures_offscreen_rendering["selection"] = self.ctx.texture(size=self.buffer_size, components=4, dtype='f4')
        self.textures_offscreen_rendering["selection"].filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.textures_offscreen_rendering["selection_depth"] = self.ctx.depth_texture(size=self.buffer_size)
        self.framebuffers["selection_fbo"] = self.ctx.framebuffer(
            color_attachments=[
                self.textures_offscreen_rendering["selection"],
            ],
            depth_attachment=self.textures_offscreen_rendering["selection_depth"],
        )

        self.samplers["depth_sampler"] = self.ctx.sampler(
            filter=(moderngl.LINEAR, moderngl.LINEAR),
            compare_func='',
        )

        # Setup fullscreen quad textures
        self.quads["fullscreen"] = ready_to_render.quad_2d(context=self.ctx,
                                                           program=self.shader_program_library["screen_quad"])
        self.quads["fullscreen"]['vao'].program["color_texture"].value = 0
        self.quads["fullscreen"]['vao'].program["normal_texture"].value = 1
        self.quads["fullscreen"]['vao'].program["viewpos_texture"].value = 2
        self.quads["fullscreen"]['vao'].program["entity_info_texture"].value = 3
        self.quads["fullscreen"]['vao'].program["selected_entity_texture"].value = 4

        return True

    def update(self, elapsed_time: float, component_pool: ComponentPool, context: moderngl.Context, event=None):

        # Initialise object on the GPU if they haven't been already

        for entity_uid, renderable in component_pool.renderable_components.items():

            mesh = component_pool.mesh_components[entity_uid]
            mesh.initialise_on_gpu(ctx=self.ctx)
            renderable.initialise_on_gpu(ctx=self.ctx,
                                         program_name_list=constants.SHADER_PASSES_LIST,
                                         shader_library=self.shader_program_library,
                                         vbo_tuple_list=mesh.get_vbo_declaration_list(),
                                         ibo_faces=mesh.ibo_faces)

        # Renderable entity IDs
        text_2d_entity_uids = list(component_pool.text_2d_components.keys())
        renderable_entity_uids = list(component_pool.renderable_components.keys())
        camera_entity_uids = list(component_pool.camera_components.keys())

        # DEBUG -HACK TODO: MOVE THIS TO THE TRANSFORM SYSTEM!!!
        for _, transform in component_pool.transform_components.items():
            transform.update()

        # Every Render pass operates on the OFFSCREEN buffers only
        for camera_uid in camera_entity_uids:

            self.forward_pass(component_pool=component_pool,
                              camera_uid=camera_uid,
                              renderable_entity_uids=renderable_entity_uids)
            self.selected_entity_pass(component_pool=component_pool,
                                      camera_uid=camera_uid,
                                      selected_entity_uid=self.selected_entity_id)
            self.text_2d_pass(component_pool=component_pool)

        # Final pass renders everything to a full screen quad from the offscreen textures
        self.render_to_screen()

    def on_event(self, event_type: int, event_data: tuple):

        if (event_type == constants.EVENT_MOUSE_BUTTON_PRESS and
                event_data[constants.EVENT_INDEX_MOUSE_BUTTON_BUTTON] == glfw.MOUSE_BUTTON_LEFT):

            # TODO: Move this to its own function!
            # Pass the coordinate of the pixel you want to sample to the fragment picking shader
            self.picker_program['texel_pos'].value = event_data[constants.EVENT_INDEX_MOUSE_BUTTON_X:]  # (x, y)
            self.textures_offscreen_rendering["entity_info"].use(location=0)

            self.picker_vao.transform(
                self.picker_buffer,
                mode=moderngl.POINTS,
                vertices=1,
                first=0,
                instances=1)
            self.selected_entity_id, instance_id, _ = struct.unpack("3i", self.picker_buffer.read())

        # FULLSCREEN VIEW MODES
        if event_type == constants.EVENT_KEYBOARD_PRESS:
            key_value = event_data[constants.EVENT_INDEX_KEYBOARD_KEY]
            if glfw.KEY_F1 <= key_value <= glfw.KEY_F11:
                self.fullscreen_selected_texture = key_value - glfw.KEY_F1

    def shutdown(self):

        # Release textures
        for texture_name, texture_obj in self.textures_offscreen_rendering.items():
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
    #                         Render functions
    # =========================================================================

    def forward_pass(self, component_pool: ComponentPool, camera_uid: int, renderable_entity_uids: list):

        # IMPORTANT: You MUST have called scene.make_renderable once before getting here!
        self.framebuffers["offscreen"].use()

        camera_component = component_pool.camera_components[camera_uid]
        camera_transform = component_pool.transform_components[camera_uid]

        # TODO: maybe move this to inside the scene?
        # Clear context (you need to use the use() first to bind it!)
        self.ctx.clear(
            red=1,
            green=1,
            blue=1,
            alpha=1.0,
            depth=1.0,
            viewport=camera_component.viewport)

        # Prepare context flags for rendering
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)  # Removing has no effect? Why?
        self.ctx.cull_face = "back"
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE)

        forward_pass_program = self.shader_program_library[constants.SHADER_PROGRAM_FORWARD_PASS]

        for uid, renderable_component in component_pool.renderable_components.items():

            if not renderable_component.visible:
                continue

            # Set camera uniforms
            camera_component.upload_uniforms(program=forward_pass_program)

            # Set entity ID
            forward_pass_program[constants.SHADER_UNIFORM_ENTITY_ID] = uid
            renderable_transform = component_pool.transform_components[uid]
            camera_transform.update()

            # Upload uniforms
            forward_pass_program["selected_entity_id"].value = uid
            forward_pass_program["entity_id"].value = uid
            forward_pass_program["view_matrix"].write(camera_transform.local_matrix.T.astype('f4').tobytes())
            forward_pass_program["model_matrix"].write(renderable_transform.local_matrix.T.astype('f4').tobytes())

            # Render the vao at the end
            renderable_component.vaos[constants.SHADER_PROGRAM_FORWARD_PASS].render(moderngl.TRIANGLES)

            # Stage: Draw transparent objects back to front

    def selected_entity_pass(self, component_pool: ComponentPool, camera_uid: int, selected_entity_uid: int):

        # IMPORTANT: It uses the current bound framebuffer!

        self.framebuffers["selection_fbo"].use()
        camera_component = component_pool.camera_components[camera_uid]
        self.ctx.clear(depth=1.0, viewport=camera_component.viewport)

        # TODO: Numbers between 0 and 1 are background colors, so we assume they are NULL selection
        if selected_entity_uid is None or selected_entity_uid <= 1:
            return

        selection_program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]

        camera_transform = component_pool.transform_components[camera_uid]

        renderable_transform = component_pool.transform_components[selected_entity_uid]

        camera_transform.update()

        program = self.shader_program_library[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS]

        # Upload uniforms
        camera_component.upload_uniforms(program=selection_program)
        program["view_matrix"].write(camera_transform.local_matrix.T.astype('f4').tobytes())
        program["model_matrix"].write(renderable_transform.local_matrix.T.astype('f4').tobytes())

        renderable_component = component_pool.renderable_components[selected_entity_uid]
        renderable_component.vaos[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS].render(moderngl.TRIANGLES)

    def text_2d_pass(self, component_pool: ComponentPool):

        if len(component_pool.text_2d_components) == 0:
            return

        self.framebuffers["offscreen"].use()

        # Upload uniforms
        projection_matrix = mat4.orthographic_projection(
            left=0,
            right=self.buffer_size[0],
            bottom=0,
            top=self.buffer_size[1],
            near=1.0,
            far=-1.0
        )
        program = self.shader_program_library[constants.SHADER_PROGRAM_TEXT_2D]
        program["projection_matrix"].write(projection_matrix)

        # Update VBOs and render text
        for uid, text_2d in component_pool.text_2d_components.items():

            self.textures_font[text_2d.font_name].use(location=0)
            text_2d.initialise_on_gpu(ctx=self.ctx, shader_library=self.shader_program_library)
            text_2d.update_buffer(font_library=self.font_library)

            text_2d.vao.render(moderngl.POINTS)

    def render_to_screen(self) -> None:

        """
        Renders selected offscreen texture to window. By default, it is the color texture, but you can
        change it using F1-F4 keys.
        :return: None
        """

        self.ctx.screen.use()
        self.ctx.screen.clear(red=1, green=1, blue=1)  # TODO: Check if this line is necessary
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.textures_offscreen_rendering["color"].use(location=0)
        self.textures_offscreen_rendering["normal"].use(location=1)
        self.textures_offscreen_rendering["viewpos"].use(location=2)
        self.textures_offscreen_rendering["entity_info"].use(location=3)
        self.textures_offscreen_rendering["selection"].use(location=4)

        quad_vao = self.quads["fullscreen"]['vao']
        quad_vao.program["selected_texture"] = self.fullscreen_selected_texture
        quad_vao.render(moderngl.TRIANGLES)

    # =========================================================================
    #                         Other Functions
    # =========================================================================

    # Release framebuffers if they already exist.
    def safe_release(self, buffer: moderngl.Buffer):
        if buffer is not None:
            buffer.release()

    def load_texture_from_file(self, texture_fpath: str, texture_id: str, datatype="f4"):
        if texture_id in self.textures_offscreen_rendering:
            raise KeyError(f"[ERROR] Texture ID '{texture_id}' already exists")

        image = Image.open(texture_fpath)
        image_data = np.array(image)
        self.textures_offscreen_rendering[texture_id] = self.ctx.texture(size=image.size,
                                                                         components=image_data.shape[-1],
                                                                         data=image_data.tobytes())

    """def offscreen_and_onscreen_pass(self, scene: Scene, viewport: Viewport):

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # =================[ Offscreen Rendering ]=====================
        self.framebuffers["offscreen"].clear()
        self.framebuffers["offscreen"].use()

        mesh_program = self.shader_library["mesh_offscreen"]

        self.upload_camera_uniforms(program=mesh_program, viewport=viewport)

        self.samplers["depth_sampler"].use(location=0)
        meshes = scene.get_nodes_by_type(node_type="mesh")
        for mesh in meshes:

            if mesh._vbo_dirty_flag:
                mesh.upload_buffers()
                mesh._vbo_dirty_flag = False

            # Upload uniforms
            mesh_program["model_matrix"].write(mesh.transform.T.astype('f4').tobytes())
            mesh.vao.render()

        self.samplers["depth_sampler"].clear(location=0)

        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.textures["diffuse"].use(location=0)
        self.quads["fullscreen"]["vao"].render()"""

    """
    def outline_pass(self, scene: Scene, viewport: Viewport):
        # print("[Renderer] _outline_pass")
        pass

    def render_shadowmap(self, scene: Scene):

        # print("[Renderer] render_shadowmap")

        if bool(flags & constants.RENDER_FLAG_DEPTH_ONLY or flags & constants.RENDER_FLAG_SEG):
            return

        for ln in scene.light_nodes:
            take_pass = False
            if (isinstance(ln.light, DirectionalLight) and
                    bool(flags & RenderFlags.SHADOWS_DIRECTIONAL)):
                take_pass = True
            elif (isinstance(ln.light, SpotLight) and
                  bool(flags & RenderFlags.SHADOWS_SPOT)):
                take_pass = True
            elif (isinstance(ln.light, PointLight) and
                  bool(flags & RenderFlags.SHADOWS_POINT)):
                take_pass = True
            if take_pass:
                self.render_pass_shadow_mapping(scene, ln, flags)
        pass
        """
