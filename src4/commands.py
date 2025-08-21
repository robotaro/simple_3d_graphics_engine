# ecs/commands.py
"""Command pattern for undo/redo"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from src4.world import World
from src4.components.transform import Transform
from src4.components.renderable import Renderable
from src4.components.hierarchy import Hierarchy


class Command(ABC):
    """Base command class for undo/redo"""

    @abstractmethod
    def execute(self):
        """Execute the command"""
        pass

    @abstractmethod
    def undo(self):
        """Undo the command"""
        pass

    @abstractmethod
    def redo(self):
        """Redo the command"""
        pass


class ModifyComponentCommand(Command):
    """Command for modifying a component's data"""

    def __init__(self, world: World, entity_id: int, component_type: type):
        self.world = world
        self.entity_id = entity_id
        self.component_type = component_type
        self.initial_state = None
        self.final_state = None

    def start(self):
        """Called when interaction starts (e.g., mouse down)"""
        component = self.world.get_component(self.entity_id, self.component_type)
        if component:
            self.initial_state = component.serialize()

    def commit(self):
        """Called when interaction ends (e.g., mouse up)"""
        component = self.world.get_component(self.entity_id, self.component_type)
        if component:
            self.final_state = component.serialize()

    def execute(self):
        """Initial execution (usually not needed as we modify live)"""
        pass

    def undo(self):
        """Restore initial state"""
        if self.initial_state:
            component = self.world.get_component(self.entity_id, self.component_type)
            if component:
                component.deserialize(self.initial_state)
                self.world.mark_dirty(self.entity_id, component.get_dirty_flags())

    def redo(self):
        """Restore final state"""
        if self.final_state:
            component = self.world.get_component(self.entity_id, self.component_type)
            if component:
                component.deserialize(self.final_state)
                self.world.mark_dirty(self.entity_id, component.get_dirty_flags())


class CommandStack:
    """Manages undo/redo stack"""

    def __init__(self, max_size: int = 100):
        self.undo_stack = []
        self.redo_stack = []
        self.max_size = max_size
        self.current_command: Optional[Command] = None

    def start_command(self, command: Command):
        """Start a new command (e.g., on mouse down)"""
        self.current_command = command
        if hasattr(command, 'start'):
            command.start()

    def commit_command(self):
        """Commit the current command (e.g., on mouse up)"""
        if self.current_command:
            if hasattr(self.current_command, 'commit'):
                self.current_command.commit()

            self.undo_stack.append(self.current_command)
            if len(self.undo_stack) > self.max_size:
                self.undo_stack.pop(0)

            self.redo_stack.clear()
            self.current_command = None

    def undo(self):
        """Undo the last command"""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        """Redo the last undone command"""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.redo()
            self.undo_stack.append(command)
