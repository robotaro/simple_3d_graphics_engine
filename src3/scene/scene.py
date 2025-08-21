"""
Main Scene class that manages all entities, hierarchy, and scene state
"""
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import pickle
import json
import moderngl
from glm import vec3, mat4

from src3.shader_loader import ShaderLoader
from src3.ubo_manager import UBOManager
from src3.scene.scene_node import SceneNode


@dataclass
class SceneSettings:
    """Scene configuration and settings"""
    name: str = "Untitled Scene"
    background_color: tuple = (0.09803921568, 0.09803921568, 0.09803921568)
    ambient_light: vec3 = vec3(0.2, 0.2, 0.2)
    fog_enabled: bool = False
    fog_color: vec3 = vec3(0.5, 0.5, 0.5)
    fog_density: float = 0.1


class Scene:
    """
    Central scene management class that handles:
    - Entity hierarchy and relationships
    - Scene queries and searches
    - Serialization/deserialization
    - Scene updates and lifecycle
    """

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 ubo_manager: UBOManager,
                 logger: Optional[logging.Logger] = None):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.ubo_manager = ubo_manager
        self.logger = logger or logging.getLogger(__name__)

        # Scene settings
        self.settings = SceneSettings()

        # Entity management
        self._next_entity_id = 1
        self._entities: Dict[int, 'Entity'] = {}  # id -> Entity
        self._root_nodes: List[SceneNode] = []
        self._node_map: Dict[int, SceneNode] = {}  # entity_id -> SceneNode

        # Special entity categories (for quick access)
        self._cameras: Set[int] = set()
        self._lights: Set[int] = set()
        self._renderables: Set[int] = set()

        # Selection state
        self._selected_entity_ids: Set[int] = set()

        # Scene state
        self._is_dirty = False
        self._update_callbacks = []

    def add_entity(self, entity: 'Entity', parent_id: Optional[int] = None) -> int:
        """
        Add an entity to the scene

        Args:
            entity: The entity to add
            parent_id: Optional parent entity ID for hierarchy

        Returns:
            The assigned entity ID
        """
        entity_id = self._next_entity_id
        self._next_entity_id += 1

        # Store entity
        self._entities[entity_id] = entity
        entity.scene_id = entity_id  # Add scene_id to entity

        # Create scene node
        node = SceneNode(entity_id=entity_id, entity=entity)
        self._node_map[entity_id] = node

        # Handle hierarchy
        if parent_id and parent_id in self._node_map:
            parent_node = self._node_map[parent_id]
            parent_node.add_child(node)
        else:
            self._root_nodes.append(node)

        # Categorize entity
        self._categorize_entity(entity_id, entity)

        # Mark scene as dirty
        self._mark_dirty()

        self.logger.debug(f"Added entity {entity.label} with ID {entity_id}")
        return entity_id

    def remove_entity(self, entity_id: int, remove_children: bool = True) -> bool:
        """
        Remove an entity from the scene

        Args:
            entity_id: ID of entity to remove
            remove_children: Whether to remove child entities

        Returns:
            True if successful
        """
        if entity_id not in self._entities:
            return False

        node = self._node_map[entity_id]

        # Handle children
        if remove_children:
            # Recursively remove children
            for child in list(node.children):
                self.remove_entity(child.entity_id, remove_children=True)
        else:
            # Reparent children to node's parent
            for child in list(node.children):
                node.remove_child(child)
                if node.parent:
                    node.parent.add_child(child)
                else:
                    self._root_nodes.append(child)

        # Remove from parent
        if node.parent:
            node.parent.remove_child(node)
        else:
            self._root_nodes.remove(node)

        # Clean up entity
        entity = self._entities[entity_id]
        if hasattr(entity, 'release'):
            entity.release()

        # Remove from collections
        del self._entities[entity_id]
        del self._node_map[entity_id]
        self._uncategorize_entity(entity_id)

        # Remove from selection
        self._selected_entity_ids.discard(entity_id)

        self._mark_dirty()
        return True

    def get_entity(self, entity_id: int) -> Optional['Entity']:
        """Get entity by ID"""
        return self._entities.get(entity_id)

    def get_entities_by_type(self, entity_type: type) -> List['Entity']:
        """Get all entities of a specific type"""
        return [e for e in self._entities.values() if isinstance(e, entity_type)]

    def get_entities_with_component(self, component_type: type) -> List['Entity']:
        """Get all entities that have a specific component type"""
        results = []
        for entity in self._entities.values():
            for attr_name in dir(entity):
                if attr_name.startswith('component_'):
                    component = getattr(entity, attr_name)
                    if isinstance(component, component_type):
                        results.append(entity)
                        break
        return results

    def select_entity(self, entity_id: int, add_to_selection: bool = False):
        """
        Select an entity

        Args:
            entity_id: Entity to select
            add_to_selection: Add to existing selection vs replace
        """
        if entity_id not in self._entities:
            return

        if not add_to_selection:
            self._selected_entity_ids.clear()

        self._selected_entity_ids.add(entity_id)
        self._mark_dirty()

    def deselect_entity(self, entity_id: int):
        """Deselect an entity"""
        self._selected_entity_ids.discard(entity_id)
        self._mark_dirty()

    def clear_selection(self):
        """Clear all selections"""
        self._selected_entity_ids.clear()
        self._mark_dirty()

    def get_selected_entities(self) -> List['Entity']:
        """Get all selected entities"""
        return [self._entities[eid] for eid in self._selected_entity_ids
                if eid in self._entities]

    def set_entity_parent(self, entity_id: int, new_parent_id: Optional[int]):
        """
        Change the parent of an entity

        Args:
            entity_id: Entity to reparent
            new_parent_id: New parent ID (None for root)
        """
        if entity_id not in self._node_map:
            return

        node = self._node_map[entity_id]

        # Remove from current parent
        if node.parent:
            node.parent.remove_child(node)
        elif node in self._root_nodes:
            self._root_nodes.remove(node)

        # Add to new parent
        if new_parent_id and new_parent_id in self._node_map:
            # Check for circular dependency
            if not self._would_create_cycle(entity_id, new_parent_id):
                new_parent = self._node_map[new_parent_id]
                new_parent.add_child(node)
            else:
                self.logger.warning(f"Cannot set parent: would create cycle")
                # Revert to root
                self._root_nodes.append(node)
        else:
            self._root_nodes.append(node)

        self._mark_dirty()

    def update(self, elapsed_time: float):
        """
        Update all entities in the scene

        Args:
            elapsed_time: Time since last update in seconds
        """
        # Update all entities
        for entity in self._entities.values():
            if hasattr(entity, 'update'):
                entity.update(elapsed_time)

        # Clear dirty flag after update
        self._is_dirty = False

        # Call update callbacks
        for callback in self._update_callbacks:
            callback(self)

    def get_render_list(self) -> List[tuple]:
        """
        Get ordered list of entities for rendering

        Returns:
            List of (entity_id, entity, world_matrix) tuples
        """
        render_list = []

        def traverse_node(node: SceneNode, parent_matrix: mat4 = mat4(1.0)):
            entity = node.entity

            # Calculate world matrix
            if entity.component_transform:
                world_matrix = parent_matrix * entity.component_transform.local_matrix
                entity.component_transform.world_matrix = world_matrix
            else:
                world_matrix = parent_matrix

            # Add to render list if renderable
            if node.entity_id in self._renderables:
                render_list.append((node.entity_id, entity, world_matrix))

            # Traverse children
            for child in node.children:
                traverse_node(child, world_matrix)

        # Start from root nodes
        for root in self._root_nodes:
            traverse_node(root)

        return render_list

    def clear(self):
        """Clear the entire scene"""
        # Release all entities
        for entity in self._entities.values():
            if hasattr(entity, 'release'):
                entity.release()

        self._entities.clear()
        self._root_nodes.clear()
        self._node_map.clear()
        self._cameras.clear()
        self._lights.clear()
        self._renderables.clear()
        self._selected_entity_ids.clear()
        self._next_entity_id = 1
        self._mark_dirty()

    def serialize(self) -> dict:
        """
        Serialize scene to dictionary

        Returns:
            Scene data as dictionary
        """
        scene_data = {
            'settings': {
                'name': self.settings.name,
                'background_color': self.settings.background_color,
                'ambient_light': list(self.settings.ambient_light),
                'fog_enabled': self.settings.fog_enabled,
                'fog_color': list(self.settings.fog_color),
                'fog_density': self.settings.fog_density
            },
            'entities': [],
            'hierarchy': []
        }

        # Serialize entities
        for entity_id, entity in self._entities.items():
            entity_data = {
                'id': entity_id,
                'type': entity.__class__.__name__,
                'label': entity.label
            }

            # Serialize components
            if entity.component_transform:
                entity_data['transform'] = {
                    'position': list(entity.component_transform.position),
                    'rotation': list(entity.component_transform.rotation),
                    'scale': list(entity.component_transform.scale)
                }

            scene_data['entities'].append(entity_data)

        # Serialize hierarchy
        def serialize_node(node: SceneNode) -> dict:
            return {
                'entity_id': node.entity_id,
                'children': [serialize_node(child) for child in node.children]
            }

        scene_data['hierarchy'] = [serialize_node(root) for root in self._root_nodes]

        return scene_data

    def deserialize(self, scene_data: dict):
        """
        Load scene from dictionary

        Args:
            scene_data: Scene data dictionary
        """
        self.clear()

        # Load settings
        settings = scene_data.get('settings', {})
        self.settings.name = settings.get('name', 'Untitled Scene')
        self.settings.background_color = tuple(settings.get('background_color', (0.1, 0.1, 0.1)))
        # ... load other settings

        # TODO: Load entities and rebuild hierarchy
        # This requires entity factory to recreate entities from serialized data

    def save_to_file(self, filepath: str):
        """Save scene to file"""
        scene_data = self.serialize()
        with open(filepath, 'w') as f:
            json.dump(scene_data, f, indent=2)

    def load_from_file(self, filepath: str):
        """Load scene from file"""
        with open(filepath, 'r') as f:
            scene_data = json.load(f)
        self.deserialize(scene_data)

    # Private helper methods

    def _categorize_entity(self, entity_id: int, entity: 'Entity'):
        """Categorize entity for quick access"""
        if entity.component_mesh or entity.component_point_cloud:
            self._renderables.add(entity_id)
        # Add more categorization as needed

    def _uncategorize_entity(self, entity_id: int):
        """Remove entity from categories"""
        self._renderables.discard(entity_id)
        self._cameras.discard(entity_id)
        self._lights.discard(entity_id)

    def _would_create_cycle(self, entity_id: int, potential_parent_id: int) -> bool:
        """Check if setting parent would create a cycle"""
        current = potential_parent_id
        while current in self._node_map:
            if current == entity_id:
                return True
            node = self._node_map[current]
            current = node.parent.entity_id if node.parent else None
        return False

    def _mark_dirty(self):
        """Mark scene as dirty (needs update)"""
        self._is_dirty = True

    @property
    def is_dirty(self) -> bool:
        """Check if scene has unsaved changes"""
        return self._is_dirty