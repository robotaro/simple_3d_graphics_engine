import os
from typing import Tuple, Dict, Optional
from src.core import constants
from logging import Logger

# Entities
from src2.entities.entity import Entity
from src2.entities.camera import Camera

# Component
from src2.components.transform import Transform


class Scene:

    def __init__(self, logger: Logger, name: Optional[str] = None, params: Optional[Dict] = None):

        self.name = name
        self.params = params if params else {}
        self.logger = logger

        self.registered_entity_types = {}
        self.registered_component_types = {}

        self.cameras = {}
        self.point_lights = {}
        self.directional_lights = {}
        self.entities = {}
        self.shared_components = {}

        self.available_entity_ids = [i for i in reversed(range(2**16))]

        # Register entities
        self.register_entity_type(name="entity", entity_class=Entity)
        self.register_entity_type(name="camera", entity_class=Camera)

        # Register components
        self.register_component_type(name="transform", component_clas=Transform)

    def register_entity_type(self, name: str, entity_class):
        if name in self.registered_entity_types:
            raise KeyError(f"[ERROR] Entity type {name} already registered")
        self.registered_entity_types[name] = entity_class

    def register_component_type(self, name: str, component_clas):
        if name in self.registered_component_types:
            raise KeyError(f"[ERROR] Component type {name} already registered")
        self.registered_component_types[name] = component_clas

    def create_entity(self, entity_type: str, name: str, params: str) -> int:

        # Generate new unique id fo r
        entity_id = self.available_entity_ids.pop()

        new_entity = self.registered_entity_types[entity_type](name=name, params=params)
        if isinstance(new_entity, Camera):
            self.cameras[entity_id] = new_entity
        elif isinstance(new_entity, Entity):
            self.entities[entity_id] = new_entity

        return entity_id

    def destroy_entity(self, entity_id: int):
        pass

    def create_shared_component(self, shared_ref: str, component_type: str, params: str) -> int:
        self.shared_components[shared_ref] = self.registered_component_types[component_type](
            name=shared_ref,
            params=params
        )

    def render(self):
        pass

    def destroy(self):
        pass
