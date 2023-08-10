from typing import Union

from ecs.components.transform_component import Transform
from ecs.components.mesh_component import Mesh
from ecs.components.mesh_component import Renderable
from ecs.components.perspective_camera_component import PerspectiveCamera


class Entity:

    def __init__(self, name=""):
        self.name = name
        self.parent = None
        self.children = []


class EntityManager:

    def __init__(self):

        self.uid_counter = 0

        # For holding states!
        self.entities = {}

        # Components
        self.transform_components = {}
        self.perspective_camera_components = {}
        self.mesh_components = {}
        self.renderable_components = {}

    def create_entity(self, name="") -> int:
        uid = self.uid_counter
        self.entities[uid] = Entity(name=name)
        self.uid_counter += 1
        return uid

    def add_component(self, entity_uid: int, component_type: str):
        if component_type == "transform":
            self.transform_components[entity_uid] = Transform()

        if component_type == "mesh":
            self.mesh_components[entity_uid] = Mesh()

        if component_type == "PerspectiveCamera":
            self.perspective_camera_components[entity_uid] = PerspectiveCamera()
