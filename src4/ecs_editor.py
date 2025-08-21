# ecs_editor.py
"""ECS-based 3D editor"""
import moderngl
import numpy as np
from glm import vec3, mat4, perspective, lookAt, radians
from application import Application
from src4.world import World
from src4.components.transform import Transform
from src4.components.in_scene import InScene
from src4.components.renderable import Renderable
from src4.components.hierarchy import Hierarchy

from src4.systems.transform_system import TransformSystem
from src4.systems.render_system import RenderSystem
from src4.resource_manager import ResourceManager
from src4.commands import CommandStack, ModifyComponentCommand


class ECSEditor(Application):
    """3D Editor built on ECS architecture"""

    title = "ECS 3D Editor"

    def initialize(self):
        """Initialize the ECS editor"""
        # Create the world
        self.world = World()

        # Create resource manager
        self.resource_manager = ResourceManager(self.ctx)

        # Create systems
        self.transform_system = TransformSystem(self.world)
        self.render_system = RenderSystem(self.world, self.ctx, self.resource_manager)

        # Command stack for undo/redo
        self.command_stack = CommandStack()

        # Editor state
        self.selected_entity = None
        self.current_scene = "default"
        self.gizmo_dragging = False

        # Setup OpenGL
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Create a simple shader and set as default
        self.create_shader()
        self.render_system.set_default_shader(self.program)

        # Create test entities
        self.create_test_scene()

        print("ECS Editor initialized!")

    def create_shader(self):
        """Create basic shader program"""
        vertex_shader = '''
        #version 330
        in vec3 in_position;
        in vec3 in_normal;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        out vec3 v_normal;
        out vec3 v_position;

        void main() {
            vec4 world_pos = model * vec4(in_position, 1.0);
            gl_Position = projection * view * world_pos;
            v_normal = mat3(transpose(inverse(model))) * in_normal;
            v_position = world_pos.xyz;
        }
        '''

        fragment_shader = '''
        #version 330
        in vec3 v_normal;
        in vec3 v_position;
        out vec4 f_color;

        uniform vec3 material_albedo;
        uniform float material_metallic;
        uniform float material_roughness;

        void main() {
            vec3 light_dir = normalize(vec3(1.0, 1.0, 1.0));
            vec3 normal = normalize(v_normal);

            // Simple lighting
            float diff = max(dot(normal, light_dir), 0.0);
            vec3 color = material_albedo * (0.3 + 0.7 * diff);

            f_color = vec4(color, 1.0);
        }
        '''

        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )

        # Register shader in resource manager
        self.resource_manager.register_shader("default", self.program)

        # Create a simple cube VAO for testing
        self.create_test_vao()

    def create_test_vao(self):
        """Create a test cube VAO"""
        vertices = np.array([
            # Front face
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
            # Back face
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0,
        ], dtype='f4')

        indices = np.array([
            0, 1, 2, 2, 3, 0,  # Front
            4, 5, 6, 6, 7, 4,  # Back
        ], dtype='i4')

        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)

        self.test_vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 3f', 'in_position', 'in_normal')],
            ibo
        )

        # Register VAO in resource manager
        self.resource_manager.register_vao("cube", self.test_vao)

    def create_test_scene(self):
        """Create some test entities"""
        # Create a parent entity
        parent = self.world.create_entity()

        # Add components to parent
        parent_transform = Transform()
        parent_transform.position = [0.0, 0.0, 0.0]
        self.world.add_component(parent, parent_transform)

        parent_hierarchy = Hierarchy()
        self.world.add_component(parent, parent_hierarchy)

        parent_renderable = Renderable()
        parent_renderable.mesh_name = "cube"
        parent_renderable.vao = self.resource_manager.get_vao("cube")
        parent_renderable.shader_program = self.program
        parent_renderable.material["albedo"] = [1.0, 0.5, 0.5]
        parent_renderable.visible = True
        self.world.add_component(parent, parent_renderable)

        self.world.add_component(parent, InScene("default"))

        # Mark parent as needing transform update
        self.world.mark_dirty(parent, ["transform"])

        # Create a child entity
        child = self.world.create_entity()

        child_transform = Transform()
        child_transform.position = [2.0, 0.0, 0.0]
        self.world.add_component(child, child_transform)

        child_hierarchy = Hierarchy()
        child_hierarchy.parent_id = parent
        parent_hierarchy.add_child(child)  # Update parent's children list
        self.world.add_component(child, child_hierarchy)

        child_renderable = Renderable()
        child_renderable.mesh_name = "cube"
        child_renderable.vao = self.resource_manager.get_vao("cube")
        child_renderable.shader_program = self.program
        child_renderable.material["albedo"] = [0.5, 0.5, 1.0]
        child_renderable.material["metallic"] = 0.8
        child_renderable.visible = True
        self.world.add_component(child, child_renderable)

        self.world.add_component(child, InScene("default"))

        # Mark child as needing transform update
        self.world.mark_dirty(child, ["transform"])

        # Create another child
        child2 = self.world.create_entity()

        child2_transform = Transform()
        child2_transform.position = [-2.0, 0.0, 0.0]
        self.world.add_component(child2, child2_transform)

        child2_hierarchy = Hierarchy()
        child2_hierarchy.parent_id = parent
        parent_hierarchy.add_child(child2)
        self.world.add_component(child2, child2_hierarchy)

        child2_renderable = Renderable()
        child2_renderable.mesh_name = "cube"
        child2_renderable.vao = self.resource_manager.get_vao("cube")
        child2_renderable.shader_program = self.program
        child2_renderable.material["albedo"] = [0.5, 1.0, 0.5]
        child2_renderable.material["roughness"] = 0.2
        child2_renderable.visible = True
        self.world.add_component(child2, child2_renderable)

        self.world.add_component(child2, InScene("default"))

        # Mark child2 as needing transform update
        self.world.mark_dirty(child2, ["transform"])

        print(f"Created entities: parent={parent}, children=[{child}, {child2}]")

        # Select the parent by default
        self.selected_entity = parent

    def update(self, time: float, delta_time: float):
        """Update and render the scene"""
        # Update systems
        self.transform_system.update(delta_time)

        # Clear screen
        self.ctx.clear(0.1, 0.1, 0.1)

        # Since we're not using a camera object, just set the matrices directly in the shader
        view = lookAt(
            vec3(5 * np.sin(time * 0.5), 3, 5 * np.cos(time * 0.5)),
            vec3(0, 0, 0),
            vec3(0, 1, 0)
        )
        projection = perspective(radians(45), self.window_size[0] / self.window_size[1], 0.1, 100)

        # Update camera in shader (we'll set this for each entity that gets rendered)
        # Store matrices for use by render system
        self.view_matrix = np.array(view, dtype='f4')
        self.projection_matrix = np.array(projection, dtype='f4')

        # Set these matrices in the default shader
        if "view" in self.program:
            self.program["view"].write(self.view_matrix.tobytes())
        if "projection" in self.program:
            self.program["projection"].write(self.projection_matrix.tobytes())

        # Render
        self.render_system.update(delta_time)

        # Debug: Show dirty sets (commented out for cleaner output)
        # if self.world.transform_dirty:
        #     print(f"Transform dirty: {self.world.transform_dirty}")

    def on_key_press(self, key: int, modifiers: int):
        """Handle key press"""
        # Undo/Redo
        if key == ord('Z') and modifiers & self.wnd.modifiers.ctrl:
            if modifiers & self.wnd.modifiers.shift:
                self.command_stack.redo()
                print("Redo")
            else:
                self.command_stack.undo()
                print("Undo")

        # Toggle visibility of selected entity
        elif key == ord('H'):
            if self.selected_entity:
                visible = self.world.get_component(self.selected_entity, Visible)
                if visible:
                    visible.visible = not visible.visible
                    self.world.mark_dirty(self.selected_entity, ["visibility"])
                    print(f"Entity {self.selected_entity} visibility: {visible.visible}")

        # Change material color of selected entity
        elif key == ord('C'):
            if self.selected_entity:
                renderable = self.world.get_component(self.selected_entity, Renderable)
                if renderable:
                    # Cycle through some colors
                    import random
                    renderable.material["albedo"] = [
                        random.random(),
                        random.random(),
                        random.random()
                    ]
                    self.world.mark_dirty(self.selected_entity, ["render"])
                    print(f"Changed color of entity {self.selected_entity}")

        # Create new entity as child of selected
        elif key == ord('N'):
            entity = self.world.create_entity()

            # Add transform
            transform = Transform()
            transform.position = [
                np.random.uniform(-2, 2),
                np.random.uniform(-2, 2),
                np.random.uniform(-2, 2)
            ]
            self.world.add_component(entity, transform)

            # Add hierarchy (child of selected or root)
            hierarchy = Hierarchy()
            if self.selected_entity:
                hierarchy.parent_id = self.selected_entity
                parent_hierarchy = self.world.get_component(self.selected_entity, Hierarchy)
                if parent_hierarchy:
                    parent_hierarchy.add_child(entity)
            self.world.add_component(entity, hierarchy)

            # Add renderable
            renderable = Renderable()
            renderable.mesh_name = "cube"
            renderable.vao = self.test_vao
            renderable.shader_program = self.program
            renderable.material["albedo"] = [
                np.random.random(),
                np.random.random(),
                np.random.random()
            ]
            self.world.add_component(entity, renderable)

            self.world.add_component(entity, Visible(True))
            self.world.add_component(entity, InScene(self.current_scene))

            print(f"Created entity {entity} as child of {self.selected_entity}")

        # Delete selected entity
        elif key == self.wnd.keys.DELETE:
            if self.selected_entity:
                # Remove from parent's children list
                hierarchy = self.world.get_component(self.selected_entity, Hierarchy)
                if hierarchy and hierarchy.parent_id:
                    parent_hierarchy = self.world.get_component(hierarchy.parent_id, Hierarchy)
                    if parent_hierarchy:
                        parent_hierarchy.remove_child(self.selected_entity)

                # Destroy entity (this also removes all its components)
                self.world.destroy_entity(self.selected_entity)
                print(f"Deleted entity {self.selected_entity}")
                self.selected_entity = None

        # Select next entity
        elif key == self.wnd.keys.TAB:
            entities = list(self.world._alive_entities)
            if entities:
                if self.selected_entity in entities:
                    idx = entities.index(self.selected_entity)
                    self.selected_entity = entities[(idx + 1) % len(entities)]
                else:
                    self.selected_entity = entities[0]
                print(f"Selected entity {self.selected_entity}")

    def on_mouse_press(self, x: int, y: int, button: int):
        """Handle mouse press"""
        if button == 1 and self.selected_entity:  # Left click
            # Start transform command
            transform = self.world.get_component(self.selected_entity, Transform)
            if transform:
                command = ModifyComponentCommand(
                    self.world,
                    self.selected_entity,
                    Transform
                )
                self.command_stack.start_command(command)
                self.gizmo_dragging = True
                print(f"Started dragging entity {self.selected_entity}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse drag"""
        if self.gizmo_dragging and self.selected_entity:
            # Live update of transform
            transform = self.world.get_component(self.selected_entity, Transform)
            if transform:
                transform.position[0] += dx * 0.01
                transform.position[1] -= dy * 0.01
                self.world.mark_dirty(self.selected_entity, ["transform"])

    def on_mouse_release(self, x: int, y: int, button: int):
        """Handle mouse release"""
        if button == 1 and self.gizmo_dragging:  # Left click
            # Commit transform command
            self.command_stack.commit_command()
            self.gizmo_dragging = False
            print(f"Committed transform for entity {self.selected_entity}")