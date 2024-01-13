import glfw
import moderngl
from PIL import Image
import numpy as np
import struct

from src.core import constants
from src.systems.system import System
from src.systems.render_system.shader_program_library import ShaderProgramLibrary
from src.systems.render_system.font_library import FontLibrary
from src.systems.render_system.render_passes.render_pass_forward import RenderPassForward
from src.systems.render_system.render_passes.render_pass_overlay import RenderPassOverlay
from src.systems.render_system.render_passes.render_pass_selection import RenderPassSelection
from src.utilities import utils_render_commands
from src.geometry_3d import ready_to_render


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
        "render_passes",
        "forward_render_pass",
        "overlay_render_pass",
        "selection_render_pass",
        "render_commands",
        "num_render_commands",
        "current_render_layer",
        "fullscreen_selected_texture",
        "debug_forward_pass_framebuffer",
        "camera_settings_ubo",
        "materials_ubo",
        "point_lights_ubo",
        "directional_lights_ubo",
        "transforms_ubo",
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
        "_sample_entity_location",
        "event_handlers",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ctx = kwargs["context"]
        self.buffer_size = kwargs["buffer_size"]
        self.shader_program_library = ShaderProgramLibrary(context=self.ctx, logger=self.logger)
        self.font_library = FontLibrary(logger=self.logger)

        # Internal components (different from normal components)
        self.framebuffers = {}
        self.textures = {}
        self.quads = {}

        self.fullscreen_selected_texture = 0  # Color is selected by default

        # Render Passes
        self.forward_render_pass = RenderPassForward(ctx=self.ctx,
                                                     shader_program_library=self.shader_program_library)
        self.overlay_render_pass = RenderPassOverlay(ctx=self.ctx,
                                                     shader_program_library=self.shader_program_library)
        self.selection_render_pass = RenderPassSelection(ctx=self.ctx,
                                                         shader_program_library=self.shader_program_library)
        self.render_passes = [
            self.forward_render_pass,
            self.overlay_render_pass,
            self.selection_render_pass]

        # Render Command variables
        self.render_commands = np.ndarray((constants.MAX_RENDER_COMMANDS,), dtype='u8')
        self.num_render_commands = 0
        self.current_render_layer = -1

        # UBOs
        self.camera_settings_ubo = None
        self.materials_ubo = None
        self.point_lights_ubo = None
        self.directional_lights_ubo = None
        self.transforms_ubo = None

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

        self._sample_entity_location = None

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

        # Setup fullscreen quad textures
        self.quads["fullscreen"] = ready_to_render.quad_2d(context=self.ctx,
                                                           program=self.shader_program_library["screen_quad"])

        # UBOs
        self.materials_ubo = self.ctx.buffer(reserve=constants.SCENE_CAMERA_SETTINGS_STRUCT_SIZE_BYTES)
        self.materials_ubo.bind_to_uniform_block(binding=constants.UBO_BINDING_CAMERA_SETTINGS)

        total_bytes = constants.SCENE_MATERIAL_STRUCT_SIZE_BYTES * constants.SCENE_MAX_NUM_MATERIALS
        self.materials_ubo = self.ctx.buffer(reserve=total_bytes)
        self.materials_ubo.bind_to_uniform_block(binding=constants.UBO_BINDING_MATERIALS)

        total_bytes = constants.SCENE_POINT_LIGHT_STRUCT_SIZE_BYTES * constants.SCENE_MAX_NUM_POINT_LIGHTS
        zero_data = np.zeros(total_bytes, dtype='uint8')
        self.point_lights_ubo = self.ctx.buffer(data=zero_data.tobytes())
        self.point_lights_ubo.bind_to_uniform_block(binding=constants.UBO_BINDING_POINT_LIGHTS)

        total_bytes = constants.SCENE_POINT_TRANSFORM_SIZE_BYTES * constants.SCENE_MAX_NUM_TRANSFORMS
        self.transforms_ubo = self.ctx.buffer(reserve=total_bytes)
        self.transforms_ubo.bind_to_uniform_block(binding=constants.UBO_BINDING_TRANSFORMS)

        self.create_framebuffers(window_size=self.buffer_size)
        return True

    def create_framebuffers(self, window_size: tuple):

        for render_pass in self.render_passes:
            render_pass.create_framebuffers(window_size=window_size)

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

        camera_pool = self.scene.get_pool(component_type=constants.COMPONENT_TYPE_CAMERA)
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
        self.forward_render_pass.texture_entity_info.use(location=0)

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
            self.selection_render_pass.framebuffer.use()
            self.selection_render_pass.framebuffer.clear(depth=1.0)
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
            self.forward_render_pass.ambient_hemisphere_light_enabled = not self.forward_render_pass.ambient_hemisphere_light_enabled
        if glfw.KEY_2 == key_value:
            self.forward_render_pass.point_lights_enabled = not self.forward_render_pass.point_lights_enabled
        if glfw.KEY_3 == key_value:
            self.forward_render_pass.directional_lights_enabled = not self.forward_render_pass.directional_lights_enabled
        if glfw.KEY_4 == key_value:
            self.forward_render_pass.gamma_correction_enabled = not self.forward_render_pass.gamma_correction_enabled
        if glfw.KEY_5 == key_value:
            self.forward_render_pass.shadows_enabled = not self.forward_render_pass.shadows_enabled

    def update(self, elapsed_time: float, context: moderngl.Context) -> bool:

        # =======================[ Render Method 1 ] =============================
        for render_pass in self.render_passes:
            render_pass.render(
                scene=self.scene,
                materials_ubo=self.materials_ubo,
                point_lights_ubo=self.point_lights_ubo,
                transforms_ubo=self.transforms_ubo,
                selected_entity_uid=self.selected_entity_id)

        # =======================[ Render Method 2 ] =============================

        #self.render_method_2()


        # Final pass renders everything to a full screen quad from the offscreen textures
        self.render_to_screen()

        return True

    def render_method_2(self):
        for entity_uid, mesh_component in self.scene.mesh.items():

            # TODO: Continue new rendering method WIP

            render_command = utils_render_commands.encode_command(
                mesh=entity_uid,
                transform=entity_uid,

            )
            g = 0
            pass

    def shutdown(self):

        for render_pass in self.render_passes:
            render_pass.release()

        for quad_name, quad in self.quads.items():
            if quad["vbo_vertices"] is not None:
                quad["vbo_vertices"].release()

            if quad["vbo_uvs"] is not None:
                quad["vbo_uvs"].release()

            if quad["vao"] is not None:
                quad["vao"].release()

        self.shader_program_library.shutdown()
        self.font_library.shutdown()

    def render_to_screen(self) -> None:

        """
        Renders selected offscreen texture to window. By default, it is the color texture, but you can
        change it using F1-F12 keys.
        :return: None
        """

        self.ctx.screen.use()
        self.ctx.screen.clear()

        self.forward_render_pass.texture_color.use(location=0)
        self.forward_render_pass.texture_normal.use(location=1)
        self.forward_render_pass.texture_viewpos.use(location=2)
        self.forward_render_pass.texture_entity_info.use(location=3)
        self.selection_render_pass.texture_color.use(location=4)
        self.overlay_render_pass.texture_color.use(location=5)
        self.forward_render_pass.texture_depth.use(location=6)

        quad_vao = self.quads["fullscreen"]['vao']
        quad_vao.program["selected_texture"] = self.fullscreen_selected_texture
        quad_vao.render(moderngl.TRIANGLES)

    def process_render_commands(self):

        # Sort commands in-place
        np.sort(self.render_commands[:self.num_render_commands], kind="mergesort")

        # Render all commands
        for i in range(self.num_render_commands):
            render_command = self.render_commands[i]
            (layer, is_transparent, distance,
             material, mesh, transform, render_mode) = utils_render_commands.decode_command(render_command)

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
