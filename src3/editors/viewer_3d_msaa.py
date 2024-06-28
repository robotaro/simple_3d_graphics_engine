import imgui
import moderngl
import struct
import copy
from glm import vec3
import numpy as np

from src3 import constants
from src3.editors.editor import Editor
from src3.components.component_factory import ComponentFactory
from src3.entities.entity_factory import EntityFactory
from src3.gizmo_3d import Gizmo3D
from src3.camera_3d import Camera3D  # Import the Camera class
from src3 import math_3d


class Viewer3DMSAA(Editor):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.window_size = (1100, 600)
        self.fbo_size = (640, 480)
        self.fbo_image_position = (0, 0)  # Indicates where on the moderngl-window the scene was rendered
        self.program = self.shader_loader.get_program(shader_filename="basic.glsl")
        self.entities = {}

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
        self.picker_output = None
        self.image_mouse_x = 0
        self.image_mouse_y = 0
        self.image_mouse_y_opengl = copy.copy(self.fbo_size[1])
        self.texture_entity_info = self.ctx.texture(size=self.fbo_size, components=3, dtype='f4')
        self.texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.selected_entity_id = -1

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

        self.gizmo_3d = Gizmo3D(ctx=self.ctx,
                                shader_loader=self.shader_loader,
                                output_fbo=self.fbo,
                                gizmo_size_on_screen=0.25)

        self.imgui_renderer.register_texture(self.fbo.color_attachments[0])

        # Debug variables
        self.debug_show_hash_colors = False
        self.debug_collision_detected = False
        self.debug_point_on_segment = vec3(0, 0, 0)
        self.debug_shortest_distance2 = 0.0

        # System-only entities
        self.renderable_entity_grid = None

    def setup(self) -> bool:

        self.entities[10] = self.entity_factory.create_renderable_3d_axis(
            axis_radius=0.05)

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

        return True

    def update(self, time: float, elapsed_time: float):

        if self.camera.right_mouse_button_down:
            self.camera.process_keyboard(elapsed_time)

        self.render_scene()
        self.render_gizmo()
        self.process_collisions()
        self.render_ui()

    def shutdown(self):
        for _, entity in self.entities.items():
            entity.release()

    def render_scene(self):

        # Setup mvp cameras
        self.program["m_proj"].write(self.camera.projection_matrix)
        self.program['m_view'].write(self.camera.view_matrix)

        # Setup lights
        self.program["light.position"].value = (10.0, 10.0, -10.0)
        self.program['light.position'].value = vec3(1.0, 1.0, 1.0)
        self.program['light.Ia'].value = vec3(0.2, 0.2, 0.2)
        self.program['light.Id'].value = vec3(0.5, 0.5, 0.5)
        self.program['light.Is'].value = vec3(1.0, 1.0, 1.0)
        self.program['camPos'].value = (0.0, 0.0, 3.0)

        self.msaa_fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.msaa_fbo.clear()

        # Render renderable entities
        for entity_id, entity in self.entities.items():
            self.program["entity_id"].value = entity_id
            self.program['m_model'].write(entity.component_transform.world_matrix)
            entity.component_mesh.render(shader_program_name="basic.glsl")

        # Resolve MSAA
        self.ctx.copy_framebuffer(self.fbo, self.msaa_fbo)

    def render_gizmo(self):

        if self.selected_entity_id not in self.entities:
            return

        self.gizmo_3d.update_and_render(
            view_matrix=self.camera.view_matrix,
            projection_matrix=self.camera.projection_matrix,
            entity_matrix=self.entities[self.selected_entity_id].component_transform.world_matrix,
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction)

    def render_ui(self):

        window_flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE
        imgui.begin("Viewer 3D MSAA", True, window_flags)
        imgui.set_window_size(self.window_size[0], self.window_size[1])

        # Left Column - Menus
        with imgui.begin_group():
            imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
            imgui.text("Entities")
            with imgui.begin_list_box("", 200, 100) as list_box:
                if list_box.opened:
                    imgui.selectable("Selected", True)
                    imgui.selectable("Not Selected", False)
            imgui.pop_style_var(1)

            imgui.text(f"Selected entity: {self.selected_entity_id}")

            activated, self.debug_show_hash_colors = imgui.checkbox("Show entity ID colors",
                                                                    self.debug_show_hash_colors)

            # DEBUG
            imgui.text("Ray Origin")
            imgui.text(str(self.camera_ray_origin))
            imgui.spacing()
            imgui.text("Ray Direction")
            imgui.text(str(self.camera_ray_direction))
            imgui.spacing()
            imgui.text("Point On segment")
            imgui.text(str(self.debug_point_on_segment))
            imgui.spacing()
            imgui.text("Euclidian shortest distance")
            imgui.text(str(np.sqrt(self.debug_shortest_distance2)))
            imgui.spacing()
            imgui.spacing()
            imgui.text("Gizmo euclidian shortest distance")
            for dist2 in self.gizmo_3d.axes_dist2:
                imgui.text(str(np.sqrt(dist2)))
            imgui.spacing()
            imgui.spacing()
            imgui.text(self.gizmo_3d.mode)
            imgui.text(str(self.gizmo_3d.active_axis))


            if activated:
                self.program["hash_color"] = self.debug_show_hash_colors

            if self.debug_collision_detected:
                imgui.text("Collision Detected!")
            else:
                imgui.text("No collision")

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
                mouse_x, mouse_y = imgui.get_mouse_pos()

                # Calculate the mouse position relative to the image
                self.image_mouse_x = mouse_x - self.fbo_image_position[0]
                self.image_mouse_y = mouse_y - self.fbo_image_position[1]

                # Generate a 3D ray from the camera position
                self.camera_ray_origin, self.camera_ray_direction = self.camera.screen_to_world(
                    self.image_mouse_x, self.image_mouse_y)


        imgui.end()

    def process_collisions(self) -> vec3:

        """
        self.entities[20] = self.entity_factory.create_sphere(
            radius=0.2,
            position=vec3(1, 1, 1),
            color=(1.0, 0.5, 0.0))

        self.entities[21] = self.entity_factory.create_sphere(
            radius=0.2,
            position=vec3(-3, 0.5, -2),
            color=(1.0, 0.5, 0.0))
        :return:
        """

        c = math_3d.intersect_ray_capsule_boolean(
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction,
            radius=0.05,
            p0=vec3(0.0, 0.0, 0.0),
            p1=vec3(1.0, 0.0, 0.0)
        )

        self.debug_point_on_segment, _ = math_3d.nearest_point_on_segment(
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction,
            p0=vec3(0.0, 0.0, 0.0),
            p1=vec3(1.0, 0.0, 0.0)
        )

        self.debug_shortest_distance2 = math_3d.distance2_ray_segment(
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction,
            p0=vec3(1.0, 1.0, 1.0),
            p1=vec3(1.0, 0.0, 0.0)
        )

        a, _, _ = math_3d.intersect_ray_sphere(
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction,
            sphere_radius=0.2,
            sphere_origin=vec3(1.0, 1.0, 1.0))

        b, _, _ = math_3d.intersect_ray_sphere(
            ray_origin=self.camera_ray_origin,
            ray_direction=self.camera_ray_direction,
            sphere_radius=0.2,
            sphere_origin=vec3(-3, 0.5, -2))

        self.debug_collision_detected = a or b or c

        #num_vertices = self.entities[20].mesh_component.num_vertices

        # Sphere
        return vec3(0, 0, 0)

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

    def handle_event_mouse_button_press(self, event_data: tuple):
        button, x, y = event_data

        if button == constants.MOUSE_RIGHT:
            self.camera.right_mouse_button_down = True

        if button == constants.MOUSE_LEFT:
            # The framebuffer image is flipped on the y-axis, so we flip the coordinates as well
            image_mouse_y_opengl = self.fbo_size[1] - self.image_mouse_y
            entity_id = self.read_entity_id(mouse_x=self.image_mouse_x,
                                            mouse_y=image_mouse_y_opengl)

            self.selected_entity_id = -1 if entity_id < 1 else entity_id

    def handle_event_mouse_button_release(self, event_data: tuple):
        button, x, y = event_data
        if button == constants.MOUSE_RIGHT:
            self.camera.right_mouse_button_down = False

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
        self.gizmo_3d.handle_event_mouse_move(event_data=event_data)

    def handle_event_mouse_drag(self, event_data: tuple):
        x, y, dx, dy = event_data
        if self.camera.right_mouse_button_down:
            self.camera.process_mouse_movement(dx=dx, dy=dy)
        self.gizmo_3d.handle_event_mouse_move(event_data=event_data)
