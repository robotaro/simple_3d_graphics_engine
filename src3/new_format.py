import time
from dataclasses import dataclass, field
from typing import Dict, Type, Any, List, Optional, Set

# =============================================================================
# 1. ENTITY & COMPONENT DEFINITIONS
# =============================================================================
# An Entity is just an integer ID. We'll use a simple counter.
Entity = int

# --- Components are simple data classes ---

# -- Spatial Components
@dataclass
class Transform:
    """Stores local position, rotation, and scale."""
    x: float = 0.0
    y: float = 0.0
    world_x: float = 0.0  # This will be calculated by the TransformSystem
    world_y: float = 0.0

@dataclass
class Parent:
    """Defines the parent in the hierarchy."""
    entity_id: Entity

@dataclass
class Children:
    """Defines the children in the hierarchy. Useful for fast traversal."""
    entity_ids: List[Entity] = field(default_factory=list)

# -- Rendering & Visibility Components
@dataclass
class Renderable:
    """A simple component to mark an entity as something to be drawn."""
    shape: str = "box"

@dataclass
class Visible:
    """The user-facing visibility state of an entity."""
    is_visible: bool = True

@dataclass
class EffectiveVisibility:
    """The calculated, final visibility state after considering ancestors."""
    is_visible: bool = True

# -- Non-Spatial Components (for the Visual Novel part)
@dataclass
class DialogueText:
    text: str

@dataclass
class NextInSequence:
    """Defines the next entity in a linear sequence, like dialogue."""
    entity_id: Entity

# -- Tag Components (have no data, just mark entities)
# These are used for logical grouping. The dirty flags have been replaced by sets.
@dataclass
class InScene:
    """Marks which logical scene an entity belongs to."""
    name: str

# =============================================================================
# 2. THE WORLD (ENTITY MANAGER)
# =============================================================================
class World:
    """
    The World acts as our central database (EntityManager). It holds all
    entities and their components. It provides a clean API for creating,
    deleting, and querying entities without exposing the underlying data storage.
    """
    def __init__(self):
        self._next_entity_id: Entity = 0
        self.components: Dict[Type, Dict[Entity, Any]] = {}
        self.entities: Set[Entity] = set()
        # --- NEW: Dirty sets for efficient state tracking ---
        # A set is used instead of a list to automatically handle duplicates.
        self.visibility_dirty_set: Set[Entity] = set()

    def create_entity(self) -> Entity:
        """Creates a new entity ID and registers it."""
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self.entities.add(entity_id)
        return entity_id

    def add_component(self, entity_id: Entity, component_instance: Any):
        """Adds a component to an entity."""
        component_type = type(component_instance)
        if component_type not in self.components:
            self.components[component_type] = {}
        self.components[component_type][entity_id] = component_instance

    def get_component(self, entity_id: Entity, component_type: Type) -> Optional[Any]:
        """Retrieves a component for a given entity."""
        return self.components.get(component_type, {}).get(entity_id)

    def has_component(self, entity_id: Entity, component_type: Type) -> bool:
        """Checks if an entity has a certain component."""
        return entity_id in self.components.get(component_type, {})

    def remove_component(self, entity_id: Entity, component_type: Type):
        """Removes a component from an entity."""
        if self.has_component(entity_id, component_type):
            del self.components[component_type][entity_id]

    def query(self, *component_types: Type) -> List[Entity]:
        """
        Finds all entities that have all of the specified component types.
        This is the core method systems will use to get the data they care about.
        """
        if not component_types:
            return list(self.entities)

        # Start with entities that have the first component type
        initial_set = set(self.components.get(component_types[0], {}).keys())
        # Intersect with entities that have the other component types
        for ct in component_types[1:]:
            initial_set.intersection_update(self.components.get(ct, {}).keys())
        return list(initial_set)

    # --- High-Level API Methods (The "SceneManager" functionality) ---

    def get_parent(self, entity_id: Entity) -> Optional[Entity]:
        parent_comp = self.get_component(entity_id, Parent)
        return parent_comp.entity_id if parent_comp else None

    def get_children(self, entity_id: Entity) -> List[Entity]:
        children_comp = self.get_component(entity_id, Children)
        return children_comp.entity_ids if children_comp else []

    def set_visibility(self, entity_id: Entity, is_visible: bool):
        """User-facing function to change visibility and trigger dirty flag."""
        print(f"\n--- ACTION: Setting visibility of Entity {entity_id} to {is_visible} ---")
        visibility_comp = self.get_component(entity_id, Visible)
        if visibility_comp:
            visibility_comp.is_visible = is_visible
            # Mark this entity and all its children as dirty by adding them to the set
            self._mark_visibility_dirty_recursive(entity_id)

    def _mark_visibility_dirty_recursive(self, entity_id: Entity):
        """Internal method to apply the dirty flag down the hierarchy."""
        self.visibility_dirty_set.add(entity_id)
        for child_id in self.get_children(entity_id):
            self._mark_visibility_dirty_recursive(child_id)


# =============================================================================
# 3. SYSTEMS
# =============================================================================
class System:
    """A base class for all systems."""
    def update(self, world: World):
        raise NotImplementedError

class VisibilitySystem(System):
    """
    Processes entities in the visibility_dirty_set to update their
    EffectiveVisibility based on their own state and their parent's.
    """
    def update(self, world: World):
        # --- MODIFIED: Directly access the dirty set ---
        if not world.visibility_dirty_set:
            return # Do nothing if no visibility has changed.

        print("[System: Visibility] Found dirty entities. Recalculating visibility...")
        # We iterate over a copy of the set in case the set is modified during iteration.
        for entity_id in list(world.visibility_dirty_set):
            visible_comp = world.get_component(entity_id, Visible)
            eff_visible_comp = world.get_component(entity_id, EffectiveVisibility)

            if not visible_comp or not eff_visible_comp:
                continue

            parent_id = world.get_parent(entity_id)
            parent_is_visible = True
            if parent_id:
                parent_eff_visible = world.get_component(parent_id, EffectiveVisibility)
                if parent_eff_visible:
                    parent_is_visible = parent_eff_visible.is_visible

            # Final visibility is a combination of its own state and its parent's
            eff_visible_comp.is_visible = visible_comp.is_visible and parent_is_visible

        # --- MODIFIED: Clean up the dirty set in one O(1) operation ---
        world.visibility_dirty_set.clear()

class TransformSystem(System):
    """Calculates world positions based on parent-child relationships."""
    def update(self, world: World):
        # In a real engine, this would also use a dirty set.
        # For simplicity, we'll just recalculate for all roots every frame.
        root_entities = [e for e in world.query(Transform) if not world.has_component(e, Parent)]

        for entity_id in root_entities:
            self._update_recursive(world, entity_id, 0.0, 0.0)

    def _update_recursive(self, world: World, entity_id: Entity, parent_wx: float, parent_wy: float):
        transform = world.get_component(entity_id, Transform)
        if not transform:
            return

        transform.world_x = transform.x + parent_wx
        transform.world_y = transform.y + parent_wy

        for child_id in world.get_children(entity_id):
            self._update_recursive(world, child_id, transform.world_x, transform.world_y)

class RenderSystem(System):
    """A simulated render system that prints visible entities in a 3D scene."""
    def update(self, world: World):
        print("[System: Render] --- Drawing 3D Scene 'Level1' ---")
        # Query for entities that are in the correct scene, are renderable, and effectively visible.
        render_targets = world.query(InScene, Renderable, EffectiveVisibility, Transform)

        for entity_id in render_targets:
            scene_tag = world.get_component(entity_id, InScene)
            if scene_tag.name != "Level1":
                continue

            eff_visibility = world.get_component(entity_id, EffectiveVisibility)
            if eff_visibility.is_visible:
                transform = world.get_component(entity_id, Transform)
                renderable = world.get_component(entity_id, Renderable)
                print(f"  - Drawing Entity {entity_id} ({renderable.shape}) at world pos ({transform.world_x:.1f}, {transform.world_y:.1f})")
        print("--- End of Frame ---")


class DialogueSystem(System):
    """A simulated system that processes non-spatial dialogue data."""
    def update(self, world: World):
        print("[System: Dialogue] --- Processing Dialogue Scene 'Intro' ---")
        dialogue_entities = world.query(InScene, DialogueText)

        # Find the start of the dialogue chain (the one not pointed to by NextInSequence)
        all_next_ids = {world.get_component(e, NextInSequence).entity_id for e in world.query(NextInSequence)}
        start_node = None
        for entity_id in dialogue_entities:
            scene_tag = world.get_component(entity_id, InScene)
            if scene_tag.name == "Intro" and entity_id not in all_next_ids:
                start_node = entity_id
                break

        # Traverse and print the dialogue
        current_node = start_node
        while current_node is not None:
            text_comp = world.get_component(current_node, DialogueText)
            print(f"  - Dialogue {current_node}: '{text_comp.text}'")
            next_comp = world.get_component(current_node, NextInSequence)
            current_node = next_comp.entity_id if next_comp else None


# =============================================================================
# 4. MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    world = World()
    systems = [
        VisibilitySystem(),
        TransformSystem(),
        DialogueSystem(), # Order doesn't matter relative to rendering
        RenderSystem()
    ]

    # --- Create Entities for the 3D Scene ("Level1") ---
    print("--- Initializing World ---")
    # Root object
    root = world.create_entity()
    world.add_component(root, Transform(x=10, y=10))
    world.add_component(root, Renderable(shape="root_node"))
    world.add_component(root, Visible())
    world.add_component(root, EffectiveVisibility())
    world.add_component(root, Children())
    world.add_component(root, InScene("Level1"))

    # Child object
    child1 = world.create_entity()
    world.add_component(child1, Transform(x=5, y=0))
    world.add_component(child1, Renderable(shape="child_box"))
    world.add_component(child1, Visible())
    world.add_component(child1, EffectiveVisibility())
    world.add_component(child1, Parent(root))
    world.add_component(child1, Children()) # Can have its own children
    world.add_component(child1, InScene("Level1"))
    world.get_component(root, Children).entity_ids.append(child1)

    # Grandchild object
    grandchild = world.create_entity()
    world.add_component(grandchild, Transform(x=0, y=2))
    world.add_component(grandchild, Renderable(shape="grandchild_sphere"))
    world.add_component(grandchild, Visible())
    world.add_component(grandchild, EffectiveVisibility())
    world.add_component(grandchild, Parent(child1))
    world.add_component(grandchild, InScene("Level1"))
    world.get_component(child1, Children).entity_ids.append(grandchild)

    # Initial visibility update for all entities
    world.set_visibility(root, True)

    # --- Create Entities for the Dialogue Scene ("Intro") ---
    d1 = world.create_entity()
    world.add_component(d1, DialogueText("Welcome to the ECS prototype."))
    world.add_component(d1, InScene("Intro"))

    d2 = world.create_entity()
    world.add_component(d2, DialogueText("It demonstrates both spatial and non-spatial data."))
    world.add_component(d2, InScene("Intro"))
    world.add_component(d1, NextInSequence(d2)) # Link d1 to d2

    d3 = world.create_entity()
    world.add_component(d3, DialogueText("Pretty neat, huh?"))
    world.add_component(d3, InScene("Intro"))
    world.add_component(d2, NextInSequence(d3)) # Link d2 to d3
    print("--- Initialization Complete ---\n")


    # --- SIMULATED GAME/EDITOR LOOP ---
    frame = 0
    while frame < 3:
        print(f"--- FRAME {frame} START ---")
        # In a real app, this would be ~60 times per second.
        for system in systems:
            system.update(world)

        # On the first frame, let's change the root's visibility
        if frame == 0:
            world.set_visibility(root, False)

        # On the second frame, let's change it back
        if frame == 1:
            world.set_visibility(root, True)

        time.sleep(1)
        frame += 1
