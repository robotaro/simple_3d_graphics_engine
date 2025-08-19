import os
import imgui
import moderngl
import struct
from itertools import accumulate
import numpy as np
from glm import vec2, vec3, vec4, inverse

from src3 import constants
from src3.gizmos import gizmo_constants
from src3.editors.editor import Editor
from src3.ubo_manager import UBOManager
from src3.components.component_factory import ComponentFactory
from src3.entities.entity_factory import EntityFactory
from src3.camera_3d import Camera3D
from src3.scene.scene_manager import SceneManager

# Gizmos
from src3.gizmos.transform_gizmo import TransformGizmo
from src3.gizmos.bezier_gizmo import BezierGizmo

SPHERE_ID = 20
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600


class Scene3DViewer(Editor):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # Extract ubo_manager from kwargs FIRST, before using it
        # The App passes these through the constructor
        self.ubo_manager = kwargs.get('ubo_manager')

        self.window_size = (1200, 750)
        self.fbo_size = (IMAGE_WIDTH, IMAGE_HEIGHT)
        self.program_basic = self.shader_loader.get_program(shader_filename="basic.glsl")
        self.program_points = self.shader_loader.get_program(shader_filename="points.glsl")

        # Create scene manager and default scene (now ubo_manager is available)
        self.scene_manager = SceneManager(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            ubo_manager=self.ubo_manager,
            logger=self.logger
        )
        self.scene = self.scene_manager.create_scene("Main Scene")

        # Factories
        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)
        self.entity_factory = EntityFactory(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            ubo_manager=self.ubo_manager
        )

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
        self.image_viewport = (0, 0, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.texture_entity_info = self.ctx.texture(size=self.fbo_size, components=3, dtype='f4')
        self.texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Create MSAA framebuffer
        self.msaa_samples = 4
        self.msaa_color_renderbuffer = self.ctx.renderbuffer(self.fbo_size, components=3, samples=self.msaa_samples)
        self.msaa_entity_info_renderbuffer = self.ctx.renderbuffer(self.fbo_size, components=3,
                                                                   samples=self.msaa_samples, dtype='f4')
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
                self.resolve_color_texture,
                self.resolve_entity_info_texture
            ],
            depth_attachment=self.ctx.depth_texture(self.fbo_size),
        )
        self.imgui_renderer.register_texture(self.fbo.color_attachments[0])

        # Gizmos
        self.transform_gizmo = TransformGizmo(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            output_fbo=self.fbo
        )
        self.transform_gizmo_mode_translation = True
        self.transform_gizmo_mode_rotation = False
        self.transform_gizmo_orientation_global = True
        self.transform_gizmo_orientation_local = False
        self.transform_gizmo.set_mode_translation()
        self.transform_gizmo.set_viewport(viewport=self.image_viewport)

        self.bezier_gizmo = BezierGizmo(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            output_fbo=self.fbo
        )

        # Debug variables
        self.debug_show_hash_colors = False
        self.debug_shortest_distance2 = 0.0

    def setup(self) -> bool:

        # ===========[ Register UBOs ]===========
        self.ubo_manager.register_ubo(
            ubo_id="mvp",
            binding_point=constants.UBO_BINDING_MVP,
            variable_names_and_sizes=[
                ("m_proj", 64),
                ("m_view", 64),
                ("m_model", 64),
                ("v_cam_pos", 3)
            ]
        )

        bezier_entity = self.entity_factory.create_bezier_curve(position=vec3(1, 0, 0))
        self.scene.add_entity(bezier_entity)

        sphere_entity = self.entity_factory.create_sphere(
            radius=0.05,
            position=vec3(1, 1, 1),
            color=(1.0, 0.5, 0.0))
        sphere_id = self.scene.add_entity(sphere_entity)

        # Load GLTF
        fpath = os.path.join(constants.RESOURCES_DIR, "meshes", "Honkai_Star_Rail_Ruan_Mei_Base_DL.gltf")
        gltf_entity = self.entity_factory.create_renderable_from_gltf(fpath=fpath)
        self.scene.add_entity(gltf_entity)

        # Add grid
        grid_entity = self.entity_factory.create_grid_xz(
            num_cells=10,
            cell_size=1.0,
            grid_color=(0.5, 0.5, 0.5)
        )
        self.scene.add_entity(grid_entity)

        # Add point cloud
        point_cloud_entity = self.entity_factory.create_point_cloud(
            points=np.random.rand(30, 3).astype('f4') + np.array(vec3(-2, 0, 0)),
            colors=np.random.rand(30, 3).astype('f4')
        )
        self.scene.add_entity(point_cloud_entity)

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
        self.ubo_manager.update_ubo(ubo_id="mvp", variable_id="m_proj", data=self.camera.projection_matrix)
        self.ubo_manager.update_ubo(ubo_id="mvp", variable_id="m_view", data=self.camera.view_matrix)
        self.ubo_manager.update_ubo(ubo_id="mvp", variable_id="v_cam_pos", data=self.camera.position)

        # Setup lights
        # TODO: Prevent re-uploading lighting information at every frame
        self.program_basic["light.position"].value = (10.0, 10.0, -10.0)
        self.program_basic['light.position'].value = vec3(1.0, 1.0, 1.0)
        self.program_basic['light.Ia'].value = vec3(0.2, 0.2, 0.2)
        self.program_basic['light.Id'].value = vec3(0.5, 0.5, 0.5)
        self.program_basic['light.Is'].value = vec3(1.0, 1.0, 1.0)

        self.msaa_fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.msaa_fbo.clear(*constants.DEFAULT_BACKGROUND_COLOR)

        # Get render list from scene
        render_list = self.scene.get_render_list()

        # Render entities
        for entity_id, entity, world_matrix in render_list:
            self.program_basic["entity_id"].value = entity_id
            self.ubo_manager.update_ubo(
                ubo_id="mvp",
                variable_id="m_model",
                data=world_matrix)
            entity.render(entity_id=entity_id)

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

        self.ubo_manager.update_ubo(ubo_id="mvp", variable_id="m_model",
                                    data=selected_entity.component_transform.world_matrix)

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

            # Replace the combo menu with radio buttons for Gizmo Mode
            imgui.text("Gizmo Mode")
            if imgui.radio_button("Translation", self.transform_gizmo_mode_translation):
                self.transform_gizmo_mode_rotation = False
                self.transform_gizmo_mode_translation = True
                self.transform_gizmo.set_mode_translation()

            if imgui.radio_button("Rotation", self.transform_gizmo_mode_rotation):
                self.transform_gizmo_mode_rotation = True
                self.transform_gizmo_mode_translation = False
                self.transform_gizmo.set_mode_rotation()
            imgui.spacing()
            imgui.spacing()

            imgui.text("Gizmo Orientation")
            if imgui.radio_button("Global", self.transform_gizmo_orientation_global):
                self.transform_gizmo_orientation_global = True
                self.transform_gizmo_orientation_local = False
                self.transform_gizmo.set_orientation_global()

            if imgui.radio_button("Local", self.transform_gizmo_orientation_local):
                self.transform_gizmo_orientation_global = False
                self.transform_gizmo_orientation_local = True
                self.transform_gizmo.set_orientation_local()
            imgui.spacing()
            imgui.spacing()

            # DEBUG
            imgui.text("Image hovering")
            imgui.text(str(self.image_hovering))
            imgui.spacing()
            imgui.spacing()
            imgui.text("Gizmo Scale")
            imgui.text(str(self.transform_gizmo.scale))
            imgui.text("Ray Origin")
            imgui.text(str(self.camera_ray_origin))
            imgui.spacing()
            imgui.text("Ray Direction")
            imgui.text(str(self.camera_ray_direction))
            imgui.spacing()
            imgui.text("Debug Plane intersections")
            imgui.text(str(self.transform_gizmo.debug_plane_intersections))
            imgui.spacing()
            imgui.spacing()
            imgui.text("Original Angle")
            imgui.text(str(self.transform_gizmo.original_rotation_angle))
            imgui.spacing()
            imgui.text("Delta Angle")
            imgui.text(str(self.transform_gizmo.debug_rotation_delta))
            imgui.spacing()

            #self.original_rotation_angle
            self.transform_gizmo.render_ui()

        if activated:
                self.program_basic["hash_color"] = self.debug_show_hash_colors

        imgui.same_line(spacing=20)

        # Right Column - 3D Scene
        with imgui.begin_group():
            texture_id = self.fbo.color_attachments[0].glo

            # Get the position where the image will be drawn
            image_position = imgui.get_cursor_screen_pos()
            self.image_viewport = (image_position[0], image_position[1], IMAGE_HEIGHT, IMAGE_WIDTH)
            self.transform_gizmo.set_viewport(viewport=self.image_viewport)

            # NOTE: I'm using the uv0 and uv1 arguments to FLIP the image back vertically, as it is flipped by default
            imgui.image(texture_id, *self.fbo.size, uv0=(0, 1), uv1=(1, 0))

            # Check if the mouse is over the image representing the rendered scene
            if imgui.is_item_hovered():
                self.image_hovering = True
                mouse_x, mouse_y = imgui.get_mouse_pos()

                # Calculate the mouse position relative to the image
                self.image_mouse_x = mouse_x - self.image_viewport[0]
                self.image_mouse_y = mouse_y - self.image_viewport[1]

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
            if self.transform_gizmo.state == gizmo_constants.GIZMO_STATE_INACTIVE:
                # The framebuffer image is flipped on the y-axis
                image_mouse_y_opengl = self.fbo_size[1] - self.image_mouse_y
                entity_id = self.read_entity_id(
                    mouse_x=self.image_mouse_x,
                    mouse_y=image_mouse_y_opengl)

                # Use scene selection
                if entity_id > 0:
                    self.scene.select_entity(entity_id)
                else:
                    self.scene.clear_selection()

            selected_entity = self.entities.get(self.selected_entity_id, None)
            model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None
            component = selected_entity.component_transform if selected_entity else None

            self.transform_gizmo.handle_event_mouse_button_press(
                event_data=(button, self.image_mouse_x, self.image_mouse_y),
                ray_direction=self.camera_ray_direction,
                ray_origin=self.camera_ray_origin,
                model_matrix=model_matrix,
                component=component)

    def handle_event_mouse_button_release(self, event_data: tuple):
        button, x, y = event_data
        if button == constants.MOUSE_RIGHT:
            self.camera.right_mouse_button_down = False

        # TODO: Getting the component is too verbose
        selected_entity = self.entities.get(self.selected_entity_id, None)
        model_matrix = selected_entity.component_transform.world_matrix if selected_entity else None
        component = selected_entity.component_transform if selected_entity else None

        if self.image_hovering:
            self.transform_gizmo.handle_event_mouse_button_release(
                event_data=event_data,
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
            self.program_basic["hash_color"] = self.debug_show_hash_colors

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
        """Shows the list of current entities in the scene"""
        imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
        imgui.text("Entities")

        with imgui.begin_list_box("", 250, 150) as list_box:
            # Render hierarchy
            def render_node(node, depth=0):
                indent = "  " * depth
                entity = node.entity
                selected = node.entity_id in self.scene._selected_entity_ids

                text = f"{indent}[{node.entity_id}] {entity.label}"
                opened, selected = imgui.selectable(text, selected)

                if selected:
                    self.scene.select_entity(node.entity_id)

                # Render children
                for child in node.children:
                    render_node(child, depth + 1)

            # Render root nodes
            for root_node in self.scene._root_nodes:
                render_node(root_node)

        imgui.pop_style_var(1)
