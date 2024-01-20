import os
from typing import Tuple, Any
from src.core import constants
from src.utilities import utils_io
import xml.etree.ElementTree as ET

from src2.entities.entity import Entity
from src2.entities.camera import Camera
from src2.components.transform import Transform


class Scene:

    def __init__(self, name: str, params: dict):

        self.name = name
        self.registered_entity_types = {}
        self.registered_component_types = {}

        self.entities = {}
        self.shared_components = {}

        self.entity_id_counter = 0
        self.component_id_counter = 0

        # Register entities
        self.register_entity_type(name=constants.ENTITY_TYPE_ENTITY, entity_class=Entity)
        self.register_entity_type(name=constants.ENTITY_TYPE_CAMERA, entity_class=Camera)

        # Register components
        self.register_component_type(name=constants.COMPONENT_TYPE_TRANSFORM, component_clas=Transform)

    def register_entity_type(self, name: str, entity_class):
        if name in self.registered_entity_types:
            raise KeyError(f"[ERROR] Entity type {name} already registered")
        self.registered_entity_types[name] = entity_class

    def register_component_type(self, name: str, component_clas):
        if name in self.registered_component_types:
            raise KeyError(f"[ERROR] Component type {name} already registered")
        self.registered_component_types[name] = component_clas

    def create_entity(self, entity_type: str, name: str, params: str) -> int:
        new_entity = self.registered_entity_types[entity_type](name=name, params=params)
        pass

    def create_shared_component(self, shared_ref: str, component_type: str, params: str) -> int:
        pass

    def render(self):
        pass

    def destroy(self):
        pass

    def from_xml(self, xml_fpath: str):
        tree = ET.parse(xml_fpath)
        root = tree.getroot()

        if root.tag != 'scene':
            raise ValueError("Invalid XML format for scene")

        # Parse shared resources
        for resource in root.findall('resource'):
            # Handle resource loading here

        # Parse shared components
        for shared_component in root.findall('shared_components/*'):
            # Handle shared component creation here

        # Parse entities
        for entity in root.findall('entity'):
            entity_name = entity.get('name', 'no_name')
            entity_type = constants.ENTITY_TYPE_ENTITY  # Assuming a default type, modify as needed
            # Extract parameters from XML and create entity
            self.create_entity(entity_type=entity_type,
                               name=entity_name,
                               params=params)

        # Handle cameras, lights, etc., similarly