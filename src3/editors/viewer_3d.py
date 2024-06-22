import imgui
import numpy as np
import moderngl
import struct
import glm
from glm import mat4, vec3

from src3.io.gltf_reader import GLTFReader
from src3.editors.editor import Editor
from src3.components.component_factory import ComponentFactory
from src3.entities.entity_factory import EntityFactory


class Viewer3D(Editor):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.window_size = (900, 600)
        self.fbo_size = (640, 480)
        self.program = self.shader_loader.get_program(shader_filename="basic.glsl")

        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)
        self.entity_factory = EntityFactory(ctx=self.ctx, shader_loader=self.shader_loader)

        # Fragment picking
        self.picker_program = self.shader_loader.get_program("fragment_picking.glsl")
        self.picker_buffer = self.ctx.buffer(reserve=3 * 4)  # 3 ints
        self.picker_vao = self.ctx.vertex_array(self.picker_program, [])
        self.picker_output = None
        self.image_mouse_x = 0
        self.image_mouse_y = 0
        self.texture_entity_info = self.ctx.texture(size=self.fbo_size, components=4, dtype='f4')
        self.texture_entity_info.filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!

        self.fbo = self.ctx.framebuffer(
            color_attachments=[
                self.ctx.texture(self.fbo_size, 3),  # Main RGB color output that will be rendered to screen
                self.texture_entity_info
            ],
            depth_attachment=self.ctx.depth_texture(self.fbo_size),
        )


        # Camera variables - temporary
        aspect_ratio = self.fbo_size[0] / self.fbo_size[1]
        self.projection_matrix = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)
        self.view_matrix = glm.inverse(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, 5.0)))

        self.camera_position = glm.vec3(0.0, 1.0, 5.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up = glm.vec3(0.0, 1.0, 0.0)
        self.camera_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = 0.0

        self.right_mouse_button_down = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.first_mouse = True

        self.entities = {}

        # System-only entities
        self.renderable_entity_grid = None

    def setup(self) -> bool:

        self.entities[1] = self.entity_factory.create_renderable_3d_axis(axis_radius=0.05)

        #gltf_fpath = os.path.join(constants.RESOURCES_DIR, "meshes", "situp_to_iddle.gltf")
        #self.entities[2] = self.load_gltf_entity(fpath=gltf_fpath)

        return True

    def load_gltf_entity(self, fpath: str):
        reader = GLTFReader()
        reader.load(gltf_fpath=fpath)
        meshes = reader.get_meshes()

        mesh_component = self.component_factory.create_mesh(
            vertices=meshes[-1]["attributes"]["POSITION"],
            normals=meshes[-1]["attributes"]["NORMAL"],
            indices=meshes[-1]["indices"].astype(np.uint32))
        transform_component = self.component_factory.create_transform()

        # Create entity
        return self.entity_factory.create_renderable(component_list=[mesh_component, transform_component])

    def update(self, time: float, elapsed_time: float):
        self.process_input(elapsed_time)
        self.render_scene()
        self.render_ui()

    def shutdown(self):
        for _, entity in self.entities.items():
            entity.release()

    def render_scene(self):

        # Setup mvp cameras
        self.program["m_proj"].write(self.projection_matrix)
        self.program['m_view'].write(self.view_matrix)
        self.program['m_model'].write(glm.mat4(1.0))

        # Setup lights
        self.program["light.position"].value = (10.0, 10.0, -10.0)
        self.program['light.position'].value = vec3(1.0, 1.0, 1.0)
        self.program['light.Ia'].value = vec3(0.2, 0.2, 0.2)
        self.program['light.Id'].value = vec3(0.5, 0.5, 0.5)
        self.program['light.Is'].value = vec3(1.0, 1.0, 1.0)
        self.program['camPos'].value = (0.0, 0.0, 3.0)

        self.fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.fbo.clear()

        # Render renderable entities
        for entity_id, entity in self.entities.items():
            self.program["entity_id"].value = entity_id
            entity.comp_mesh.render(shader_program_name="basic.glsl")

    def render_ui(self):
        imgui.begin("Viewer 3D", True)
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

        imgui.same_line(spacing=20)

        # Right Column - 3D Scene
        with imgui.begin_group():
            texture_id = self.fbo.color_attachments[0].glo

            # Get the position where the image will be drawn
            image_pos = imgui.get_cursor_screen_pos()

            # NOTE: I'm using the uv0 and uv1 arguments to FLIP the image back vertically, as it is flipped by default
            imgui.image(texture_id, *self.fbo.size, uv0=(0, 1), uv1=(1, 0))

            # Check if the mouse is over the image and print the position
            if imgui.is_item_hovered():
                mouse_x, mouse_y = imgui.get_mouse_pos()

                # Calculate the mouse position relative to the image
                self.image_mouse_x = mouse_x - image_pos[0]
                self.image_mouse_y = mouse_y - image_pos[1]

                # TODO: Window rays will be cast from here
                #if 0 <= self.image_mouse_x <= self.fbo_size[0] and 0 <= self.image_mouse_y <= self.fbo_size[1]:
                #
                #   print(f"Mouse position over image: ({image_mouse_x}, {image_mouse_y})")
                #   pass

        imgui.end()

    def process_input(self, elapsed_time):
        io = imgui.get_io()

        if self.right_mouse_button_down:
            # Mouse movement
            mouse_x, mouse_y = io.mouse_pos

            if self.first_mouse:
                self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y
                self.first_mouse = False

            x_offset = (mouse_x - self.last_mouse_x) * self.mouse_sensitivity
            y_offset = (self.last_mouse_y - mouse_y) * self.mouse_sensitivity
            self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y

            self.yaw += x_offset
            self.pitch += y_offset

            self.pitch = max(-89.0, min(89.0, self.pitch))

            front = glm.vec3()
            front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
            front.y = np.sin(glm.radians(self.pitch))
            front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
            self.camera_front = glm.normalize(front)

            # Keyboard movement
            if io.keys_down[ord('W')]:
                self.camera_position += self.camera_speed * elapsed_time * self.camera_front
            if io.keys_down[ord('S')]:
                self.camera_position -= self.camera_speed * elapsed_time * self.camera_front
            if io.keys_down[ord('E')]:
                self.camera_position += self.camera_speed * elapsed_time * vec3(0, 1, 0)
            if io.keys_down[ord('Q')]:
                self.camera_position -= self.camera_speed * elapsed_time * vec3(0, 1, 0)
            if io.keys_down[ord('A')]:
                self.camera_position -= glm.normalize(
                    glm.cross(self.camera_front, self.camera_up)) * self.camera_speed * elapsed_time
            if io.keys_down[ord('D')]:
                self.camera_position += glm.normalize(
                    glm.cross(self.camera_front, self.camera_up)) * self.camera_speed * elapsed_time

            self.view_matrix = glm.lookAt(self.camera_position, self.camera_position + self.camera_front,
                                          self.camera_up)

    def get_entity_id(self, mouse_x, mouse_y) -> int:

        # The mouse positions are on the framebuffer being rendered, not the screen coordinates
        self.picker_program['texel_pos'].value = (int(mouse_x), int(mouse_y))  # (x, y)
        self.texture_entity_info.use(location=0)

        self.picker_vao.transform(
            self.picker_buffer,
            mode=moderngl.POINTS,
            vertices=1,
            first=0,
            instances=1)

        entity_id, instance_id, _ = struct.unpack("3i", self.picker_buffer.read())
        return entity_id

    def handle_event_mouse_button_press(self, event_data: tuple):
        button, _, x, _, y = event_data
        if button == imgui.MOUSE_BUTTON_RIGHT:
            self.right_mouse_button_down = True
            self.first_mouse = True
            self.last_mouse_x, self.last_mouse_y = x, y

        if button == imgui.MOUSE_BUTTON_LEFT:
            entity_id = self.get_entity_id(mouse_x=self.image_mouse_x, mouse_y=self.image_mouse_y)
            print(self.image_mouse_x, self.image_mouse_y, entity_id)

    def handle_event_mouse_button_release(self, event_data: tuple):
        button, _, x, _, y = event_data
        if button == imgui.MOUSE_BUTTON_RIGHT:
            self.right_mouse_button_down = False
            self.first_mouse = True

    def handle_event_mouse_move(self, event_data: tuple):
        x, _, y = event_data
        if self.right_mouse_button_down:
            x_offset = (x - self.last_mouse_x) * self.mouse_sensitivity
            y_offset = (self.last_mouse_y - y) * self.mouse_sensitivity
            self.last_mouse_x, self.last_mouse_y = x, y

            self.yaw += x_offset
            self.pitch += y_offset

            self.pitch = max(-89.0, min(89.0, self.pitch))

            front = glm.vec3()
            front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
            front.y = np.sin(glm.radians(self.pitch))
            front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
            self.camera_front = glm.normalize(front)
            self.view_matrix = glm.lookAt(self.camera_position, self.camera_position + self.camera_front,
                                          self.camera_up)
