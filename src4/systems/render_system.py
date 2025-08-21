import moderngl
from typing import Dict, Optional

from src4.systems.system import System
from src4.world import World
from src4.components.transform import Transform
from src4.components.renderable import Renderable
from src4.components.hierarchy import Hierarchy


class RenderSystem(System):
    """Handles rendering of all visible entities"""

    def __init__(self, world: World, ctx, resource_manager=None):
        super().__init__(world)
        self.ctx = ctx
        self.resource_manager = resource_manager  # For loading VAOs, textures, shaders
        self.camera = None
        self.default_shader = None
        super().__init__(world)
        self.ctx = ctx
        self.resource_manager = resource_manager  # For loading VAOs, textures, shaders
        self.camera = None
        self.default_shader = None

    def set_camera(self, camera):
        self.camera = camera

    def set_default_shader(self, shader):
        self.default_shader = shader

    def update(self, delta_time: float):
        """Render all visible entities in the current scene"""
        # Process any pending render updates (e.g., loading resources)
        self.process_dirty_entities("render", self._update_renderable)

        # Get all renderable entities
        renderable = self.world.get_entities_with_components(Transform, Renderable)

        # Sort by render order for transparency
        sorted_entities = sorted(renderable,
                                 key=lambda e: self._get_render_order(e))

        for entity_id in sorted_entities:
            self._render_entity(entity_id)

    def _update_renderable(self, entity_id: int):
        """Update renderable resources (load VAO, textures, etc.)"""
        renderable = self.world.get_component(entity_id, Renderable)
        if not renderable:
            return

        # Load resources if resource manager is available
        if self.resource_manager:
            # Load VAO if needed
            if not renderable.vao and renderable.mesh_name:
                renderable.vao = self.resource_manager.get_vao(renderable.mesh_name)

            # Load shader if needed
            if not renderable.shader_program:
                if renderable.shader_name and renderable.shader_name != "default":
                    renderable.shader_program = self.resource_manager.get_shader(renderable.shader_name)
                else:
                    renderable.shader_program = self.default_shader

            # Load textures if needed
            for slot, texture_name in renderable.texture_names.items():
                if texture_name and slot not in renderable.textures:
                    texture = self.resource_manager.get_texture(texture_name)
                    if texture:
                        renderable.textures[slot] = texture

    def _get_render_order(self, entity_id: int) -> int:
        """Get render order for sorting"""
        renderable = self.world.get_component(entity_id, Renderable)
        return renderable.render_order if renderable else 0

    def _render_entity(self, entity_id: int):
        """Render a single entity"""
        transform = self.world.get_component(entity_id, Transform)
        renderable = self.world.get_component(entity_id, Renderable)

        if not transform or not renderable or not renderable.vao:
            return

        # Check if transform has been calculated
        if transform.world_matrix is None:
            return

        # Check visibility (including parent visibility)
        if not self._is_visible(entity_id):
            return

        # Use entity's shader or default
        shader = renderable.shader_program or self.default_shader
        if not shader:
            return

        # Set view and projection matrices in the shader
        # These should already be set in the default shader, but if using a custom shader, set them
        # Since we're using the same shader for all entities in this example, this is already handled

        # Apply renderable uniforms (includes world matrix and materials)
        renderable.apply_uniforms(transform.world_matrix)

        # Set render states
        if renderable.cull_face:
            self.ctx.enable(moderngl.CULL_FACE)
        else:
            self.ctx.disable(moderngl.CULL_FACE)

        # Render
        renderable.vao.render()

    def _is_visible(self, entity_id: int) -> bool:
        """Check if entity is visible (including parent hierarchy)"""
        renderable = self.world.get_component(entity_id, Renderable)
        if not renderable or not renderable.visible:
            return False

        # Check parent visibility recursively
        hierarchy = self.world.get_component(entity_id, Hierarchy)
        if hierarchy and hierarchy.parent_id:
            return self._is_visible(hierarchy.parent_id)

        return True