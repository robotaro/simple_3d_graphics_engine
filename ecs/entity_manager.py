from typing import Union

from ecs.components.component import Component
from ecs.components.transform_component import Transform
from ecs.components.mesh_component import Mesh
from ecs.components.renderable_component import Renderable
from ecs.components.perspective_camera_component import PerspectiveCamera

class Entity:

    def __init__(self, name=""):
        self.name = name
        self.parent = None
        self.children = []


class EntityManager:

    COMPONENT_TYPE_MAP = {
        "transform": Transform,
        "mesh": Mesh,
        "renderable": Renderable,
        "perspective_camera": PerspectiveCamera
    }

    def __init__(self):

        self.uid_counter = 0

        # For holding states!
        self.entities = {}

        # Components
        self.transform_components = {}
        self.perspective_camera_components = {}
        self.mesh_components = {}
        self.renderable_components = {}

        self.component_storage_map = {
            Transform: self.transform_components,
            Mesh: self.mesh_components,
            Renderable: self.renderable_components,
            PerspectiveCamera: self.perspective_camera_components
        }

    def create_entity(self, name="") -> int:
        uid = self.uid_counter
        self.entities[uid] = Entity(name=name)
        self.uid_counter += 1
        return uid

    def add_component(self, entity_uid: int, component: Component):
        storage = self.component_storage_map.get(type(component), None)
        self.component_storage_map[storage][entity_uid] = component

    def get_components(self, entity_uid: int) -> list:
        components = []
        for _, storage in self.component_storage_map.items():
            if entity_uid in storage:
                components.append(storage)
        return components

