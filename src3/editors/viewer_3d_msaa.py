import imgui
import moderngl
import struct
from itertools import accumulate
import numpy as np
from glm import vec3, vec4, inverse

from src3 import constants
from src3.editors.editor import Editor
from src3.components.component_factory import ComponentFactory
from src3.entities.entity_factory import EntityFactory
from src3.camera_3d import Camera3D  # Import the Camera class

# Gizmos
from src3.gizmos.transform_gizmo import TransformGizmo
from src3.gizmos.bezier_gizmo import BezierGizmo


class Viewer3DMSAA(Editor):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.window_size = (1100, 600)
        self.fbo_size = (640, 480)
        self.fbo_image_position = (0, 0)  # Indicates where on the moderngl-window the scene was rendered
        self.program = self.shader_loader.get_program(shader_filename="basic.glsl")
        self.entities = {}
        self.selected_entity_id = -1

        # Uniform Blocks
        self.ubo_mvp_sizes = {
            'm_proj': 64,
            'm_view': 64,
            'm_model': 64
        }
        # Calculate uniform buffer size while taking into account 16bytes memory alignment
        min_size = sum(self.ubo_mvp_sizes.values())
        buffer_size = min_size if not min_size % 16 else ((min_size // 16) + 1) * 16
        self.ubo_mvp_offsets = dict(zip(self.ubo_mvp_sizes, accumulate(self.ubo_mvp_sizes.values(), initial=0)))
        self.ubo_mvp = self.ctx.buffer(reserve=buffer_size)
        self.ubo_mvp.bind_to_uniform_block(binding=constants.UBO_BINDING_MVP)

        # Factories
        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)
        self.entity_factory = EntityFactory(ctx=self.ctx, shader_loader=self.shader_loader)

        # Camera variables
        self.camera = Camera3D(fbo_size=self.fbo_size, position=vec3(0, 1, 5))
        self.camera_ray_origin = vec3(1E9, 1E9, 1E9)
        self.camera_ray_direction = vec3(0, 1, 0)

        # Fragment picking
        self.picker_program = self.shader_loader.get_program("fragment_picking.glsl")
        self.picker_buffer = self.ctx.buffer(reserve=3 * 4)  # 3 ints
        self.picker_vao = self.ctx.vertex_array(self.picker_program, [])
        self.image_hovering = False
        self.image_mouse_x = 0  # Current position of mouse on rendered image
        self.image_mouse_y = 0
        self.texture_entity_info = self.ctx.texture(size=self.fbo_size, components=3, dtype='f4')
        self.texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!

        # Create MSAA framebuffer
        self.msaa_samples = 4
        self.msaa_color_renderbuffer = self.ctx.renderbuffer(self.fbo_size, components=3, samples=self.msaa_samples)
        self.msaa_entity_info_renderbuffer = self.ctx.renderbuffer(self.fbo_size, components=3, samples=self.msaa_samples, dtype='f4')
        self.msaa_depth_renderbuffer = self.ctx.depth_renderbuffer(self.fbo_size, samples=self.msaa_samples)
        self.msaa_fbo = self.ctx.framebuffer(
            color_attachments=[self.msaa_color_renderbuffer, self.msaa_entity_info_renderbuffer],
            depth_attachment=self.msaa_depth_renderbuffer,
        )

        # Create final framebuffer
        self.resolve_color_texture = self.ctx.texture(self.fbo_size, 3)
        self.resolve_entity_info_texture = self.ctx.texture(self.fbo_size, components=3, dtype='f4')
        self.fbo = self.ctx.framebuffer(
            color_attachments=[
                self.resolve_color_texture,  # Main RGB color output that will be rendered to screen
                self.resolve_entity_info_texture  # Entity info output
            ],
            depth_attachment=self.ctx.depth_texture(self.fbo_size),
        )
        self.imgui_renderer.register_texture(self.fbo.color_attachments[0])

        # Gizmos
        self.gizmo_3d_mode_index = 0
        self.transform_gizmo = TransformGizmo(ctx=self.ctx,
                                              shader_loader=self.shader_loader,
                                              output_fbo=self.fbo)
        self.bezier_gizmo = BezierGizmo(ctx=self.ctx,
                                        shader_loader=self.shader_loader,
                                        output_fbo=self.fbo)
        # Debug variables
        self.debug_show_hash_colors = False
        self.debug_point_on_segment = vec3(0, 0, 0)
        self.debug_shortest_distance2 = 0.0

        # System-only entities
        self.renderable_entity_grid = None

    def setup(self) -> bool:

        self.entities[10] = self.entity_factory.create_bezier_curve()

        self.entities[20] = self.entity_factory.create_sphere(
            radius=0.2,
            position=vec3(1, 1, 1),
            color=(1.0, 0.5, 0.0))

        self.entities[21] = self.entity_factory.create_sphere(
            radius=0.2,
            position=vec3(-3, 0.5, -2),
            color=(1.0, 0.5, 0.0))

        self.entities[30] = self.entity_factory.create_grid_xz(
            num_cells=10,
            cell_size=1.0,
            grid_color=(0.5, 0.5, 0.5)
        )

        self.entities[40] = self.entity_factory.create_point_cloud(
            points=np.random.rand(30, 3).astype('f4'),
            colors=np.random.rand(30, 3).astype('f4')
        )

        return True

    def update(self, time: float, elapsed_time: float):

        if self.camera.right_mouse_button_down:
            self.camera.process_keyboard(elapsed_time)

        self.render_scene()
        self.render_gizmos()
        self.render_ui()

    def shutdown(self):
        for _, entity in self.entities.items():
            entity.release()

        self.transform_gizmo.release()

    def render_scene(self):

        # Common UBO settings
        self.ubo_mvp.write(data=self.camera.projection_matrix, offset=self.ubo_mvp_offsets['m_proj'])
        self.ubo_mvp.write(data=self.camera.view_matrix, offset=self.ubo_mvp_offsets['m_view'])

        # ============[ Render meshes ]================

        # Setup lights
        self.program["light.position"].value = (10.0, 10.0, -10.0)
        self.program['light.position'].value = vec3(1.0, 1.0, 1.0)
        self.program['light.Ia'].value = vec3(0.2, 0.2, 0.2)
        self.program['light.Id'].value = vec3(0.5, 0.5, 0.5)
        self.program['light.Is'].value = vec3(1.0, 1.0, 1.0)
        self.program['camPos'].value = (0.0, 0.0, 3.0)

        self.msaa_fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.msaa_fbo.clear(*constants.DEFAULT_BACKGROUND_COLOR)

        # Render entities
        for entity_id, entity in self.entities.items():
            self.program["entity_id"].value = entity_id
            self.ubo_mvp.write(data=entity.component_transform.world_matrix, offset=self.ubo_mvp_offsets['m_model'])

            if entity.component_mesh:
                entity.component_mesh.render(shader_program_name="basic.glsl")

        # ==========[ Render point clouds ]============

        self.ctx.enable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = 'auto'

        # Setup mvp cameras
        pc_program = self.shader_loader.get_program("points.glsl")

        pc_program['cam_pos'].write(vec3(inverse(self.camera.view_matrix)[3]))

        # Render entities
        for entity_id, entity in self.entities.items():
            self.ubo_mvp.write(data=entity.component_transform.world_matrix, offset=self.ubo_mvp_offsets['m_model'])

            if entity.component_point_cloud:
                entity.component_point_cloud.render()

        self.ctx.disable(flags=moderngl.PROGRAM_POINT_SIZE)
        self.ctx.gc_mode = None

        # Resolve MSAA
        self.ctx.copy_framebuffer(self.fbo, self.msaa_fbo)

    def render_gizmos(self):

        if self.selected_entity_id not in self.entities:
            return

        selected_entity = self.entities[self.selected_entity_id]

        self.transform_gizmo.render(
            view_matrix=self.camera.view_matrix,
            projection_matrix=self.camera.projection_matrix,
            model_matrix=selected_entity.component_transform.world_matrix,
            component=selected_entity.component_transform
        )

        self.bezier_gizmo.render(
            view_matrix=self.camera.view_matrix,
            projection_matrix=self.camera.projection_matrix,
            model_matrix=selected_entity.component_transform.world_matrix,
            component=selected_entity.component_bezier_segment
        )

    def render_ui(self):

        window_flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE
        imgui.begin("Viewer 3D MSAA", True, window_flags)
        imgui.set_window_size(self.window_size[0], self.window_size[1])

        # Left Column - Menus
        with imgui.begin_group():
            self.render_ui_entity_list()

            activated, self.debug_show_hash_colors = imgui.checkbox("Show entity ID colors",
                                                                    self.debug_show_hash_colors)

            imgui.push_item_width(120)
            clicked, self.gizmo_3d_mode_index = imgui.combo(
                "Gizmo Mode", self.gizmo_3d_mode_index,
                [constants.GIZMO_MODE_TRANSLATION,
                 constants.GIZMO_MODE_ROTATION]
            )
            if clicked:
                self.transform_gizmo.gizmo_mode = constants.GIZMO_MODES[self.gizmo_3d_mode_index]

            # DEBUG
            imgui.text("Image hovering")
            imgui.text(str(self.image_hovering))
            imgui.spacing()
            imgui.spacing()
            imgui.text("Gizmo Scale")
            imgui.text(str(self.transform_gizmo.gizmo_scale))
            imgui.text("Ray Origin")
            imgui.text(str(self.camera_ray_origin))
            imgui.spacing()
            imgui.text("Ray Direction")
            imgui.text(str(self.camera_ray_direction))
            imgui.spacing()
            self.transform_gizmo.render_ui()

        if activated:
                self.program["hash_color"] = self.debug_show_hash_colors

        imgui.same_line(spacing=20)

        # Right Column - 3D Scene
        with imgui.begin_group():
            texture_id = self.fbo.color_attachments[0].glo

            # Get the position where the image will be drawn
            self.fbo_image_position = imgui.get_cursor_screen_pos()

            # NOTE: I'm using the uv0 and uv1 arguments to FLIP the image back vertically, as it is flipped by default
            imgui.image(texture_id, *self.fbo.size, uv0=(0, 1), uv1=(1, 0))

            # Check if the mouse is over the image representing the rendered scene
            if imgui.is_item_hovered():
                self.image_hovering = True
                mouse_x, mouse_y = imgui.get_mouse_pos()

                # Calculate the mouse position relative to the image
                self.image_mouse_x = mouse_x - self.fbo_image_position[0]
                self.image_mouse_y = mouse_y - self.fbo_image_position[1]

                # Generate a 3D ray from the camera position
                self.camera_ray_origin, self.camera_ray_direction = self.camera.screen_to_world(
                    self.image_mouse_x, self.image_mouse_y)
            else:
                self.image_hovering = False

        imgui.show_demo_window()

        imgui.end()

    def read_entity_id(self, mouse_x, mouse_y) -> int:

        # Only read an entity ID if

        # The mouse positions are on the framebuffer being rendered, not the screen coordinates
        self.picker_program['texel_pos'].value = (int(mouse_x), int(mouse_y))  # (x, y)
        self.resolve_entity_info_texture.use(location=0)

        self.picker_vao.transform(
            self.picker_buffer,
            mode=moderngl.POINTS,
            vertices=1,
            first=0,
            instances=1)

        entity_id, instance_id, _ = struct.unpack("3i", self.picker_buffer.read())
        # NOTE: Entity ID is being shown on the gui already
        return entity_id

    # =========================================================================
    #                           Input Callbacks
    # =========================================================================

    def handle_event_mouse_button_press(self, event_data: tuple):
        button, x, y = event_data

        if button == constants.MOUSE_RIGHT:
            self.camera.right_mouse_button_down = True

        if self.image_hovering and button == constants.MOUSE_LEFT:

            # You can only select another entity if, when you click, you are not hovering the gizmo
            if self.transform_gizmo.state == constants.GIZMO_STATE_INACTIVE:

                # The framebuffer image is flipped on the y-axis, so we flip the coordinates as well
                image_mouse_y_opengl = self.fbo_size[1] - self.image_mouse_y
                entity_id = self.read_entity_id(mouse_x=self.image_mouse_x,
                                                mouse_y=image_mouse_y_opengl)

                self.selected_entity_id = -1 if entity_id < 1 else entity_id

            selected_entity = self.entities.get(self.selected_entity_id, None)
            model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None
            component = selected_entity.component_transform if selected_entity else None

            self.transform_gizmo.handle_event_mouse_button_press(
                button=button,
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=component)

    def handle_event_mouse_button_release(self, event_data: tuple):
        button, x, y = event_data
        if button == constants.MOUSE_RIGHT:
            self.camera.right_mouse_button_down = False

        selected_entity = self.entities.get(self.selected_entity_id, None)
        model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None
        component = selected_entity.component_transform if selected_entity else None

        if self.image_hovering:
            self.transform_gizmo.handle_event_mouse_button_release(
                button=button,
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=component)

    def handle_event_keyboard_press(self, event_data: tuple):
        key, modifiers = event_data

        self.camera.handle_key_press(key=key, modifiers=modifiers)

    def handle_event_keyboard_release(self, event_data: tuple):
        key, modifiers = event_data

        # DEBUG
        if key == ord("h"):
            self.debug_show_hash_colors = not self.debug_show_hash_colors
            self.program["hash_color"] = self.debug_show_hash_colors

        self.camera.handle_key_release(key)

    def handle_event_mouse_double_click(self, event_data: tuple):
        print("Double click!")

    def handle_event_mouse_move(self, event_data: tuple):
        x, y, dx, dy = event_data

        # TODO: Revise this logic. It is superfluous
        selected_entity = self.entities.get(self.selected_entity_id, None)
        model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None

        if self.image_hovering and selected_entity:

            self.bezier_gizmo.handle_event_mouse_move(
                event_data=event_data,
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=selected_entity.component_bezier_segment
            )

            self.transform_gizmo.handle_event_mouse_move(
                event_data=event_data,
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=selected_entity.component_transform
            )

    def handle_event_mouse_drag(self, event_data: tuple):
        x, y, dx, dy = event_data
        if self.camera.right_mouse_button_down:
            self.camera.process_mouse_movement(dx=dx, dy=dy)

        selected_entity = self.entities.get(self.selected_entity_id, None)
        model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None
        component = selected_entity.component_transform if selected_entity else None
        if self.image_hovering:
            new_model_matrix = self.transform_gizmo.handle_event_mouse_drag(
                event_data=event_data,
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=component)

            if selected_entity is not None:
                selected_entity.component_transform.update_world_matrix(world_matrix=new_model_matrix)

    # ======================================================================
    #                             UI Functions
    # ======================================================================

    def render_ui_entity_list(self):
        """
        Shows the list of current entities in the scene, and which entity is actively selected
        :return:
        """
        imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
        imgui.text("Entities")
        with imgui.begin_list_box("", 250, 150) as list_box:
            for entity_id, entity in self.entities.items():
                text = f"[{entity_id}] {entity.label}"
                if self.selected_entity_id == entity_id:
                    imgui.selectable(text, True)
                    continue
                opened, selected = imgui.selectable(text, False)
                if selected:
                    self.selected_entity_id = entity_id
        imgui.pop_style_var(1)
