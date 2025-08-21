# ecs/world.py
"""The World container - central database for all entities and components"""
from typing import Dict, Set, List, Type, Optional, Any
from collections import defaultdict
import json


class World:
    """
    The central ECS world containing all entities and components.
    Acts as the primary API for all entity/component manipulation.
    """

    def __init__(self):
        # Entity management
        self._next_entity_id = 1
        self._alive_entities: Set[int] = set()

        # Component storage: component_type -> entity_id -> component_instance
        self._components: Dict[Type, Dict[int, Any]] = defaultdict(dict)

        # Dirty sets for event-driven updates
        self.transform_dirty: Set[int] = set()
        self.hierarchy_dirty: Set[int] = set()
        self.render_dirty: Set[int] = set()

        # Named dirty sets for custom use
        self._dirty_sets: Dict[str, Set[int]] = defaultdict(set)

    def create_entity(self) -> int:
        """Create a new entity and return its ID"""
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self._alive_entities.add(entity_id)
        return entity_id

    def destroy_entity(self, entity_id: int):
        """Destroy an entity and all its components"""
        if entity_id not in self._alive_entities:
            return

        # Remove all components
        for component_dict in self._components.values():
            component_dict.pop(entity_id, None)

        # Remove from all dirty sets
        for dirty_set in self._dirty_sets.values():
            dirty_set.discard(entity_id)
        self.transform_dirty.discard(entity_id)
        self.hierarchy_dirty.discard(entity_id)
        self.render_dirty.discard(entity_id)

        self._alive_entities.remove(entity_id)

    def add_component(self, entity_id: int, component: 'Component'):
        """Add a component to an entity"""
        if entity_id not in self._alive_entities:
            raise ValueError(f"Entity {entity_id} does not exist")

        component_type = type(component)
        self._components[component_type][entity_id] = component

        # Mark entity as dirty for relevant systems
        self.mark_dirty(entity_id, component.get_dirty_flags())

    def remove_component(self, entity_id: int, component_type: Type):
        """Remove a component from an entity"""
        if component_type in self._components:
            self._components[component_type].pop(entity_id, None)

    def get_component(self, entity_id: int, component_type: Type) -> Optional[Any]:
        """Get a component from an entity"""
        return self._components.get(component_type, {}).get(entity_id)

    def has_component(self, entity_id: int, component_type: Type) -> bool:
        """Check if an entity has a component"""
        return entity_id in self._components.get(component_type, {})

    def get_entities_with_component(self, component_type: Type) -> Set[int]:
        """Get all entities that have a specific component type"""
        return set(self._components.get(component_type, {}).keys())

    def get_entities_with_components(self, *component_types: Type) -> Set[int]:
        """Get all entities that have ALL specified component types"""
        if not component_types:
            return set()

        result = self.get_entities_with_component(component_types[0])
        for component_type in component_types[1:]:
            result &= self.get_entities_with_component(component_type)
        return result

    def mark_dirty(self, entity_id: int, flags: List[str]):
        """Mark an entity as dirty for specific systems"""
        for flag in flags:
            if flag == "transform":
                self.transform_dirty.add(entity_id)
            elif flag == "hierarchy":
                self.hierarchy_dirty.add(entity_id)
            elif flag == "render":
                self.render_dirty.add(entity_id)
            else:
                self._dirty_sets[flag].add(entity_id)

    def clear_dirty(self, flag: str):
        """Clear a specific dirty set"""
        if flag == "transform":
            self.transform_dirty.clear()
        elif flag == "hierarchy":
            self.hierarchy_dirty.clear()
        elif flag == "render":
            self.render_dirty.clear()
        else:
            self._dirty_sets[flag].clear()

    def get_dirty_set(self, flag: str) -> Set[int]:
        """Get a specific dirty set"""
        if flag == "transform":
            return self.transform_dirty
        elif flag == "hierarchy":
            return self.hierarchy_dirty
        elif flag == "render":
            return self.render_dirty
        else:
            return self._dirty_sets[flag]