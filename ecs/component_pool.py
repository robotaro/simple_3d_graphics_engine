from typing import Union

from ecs import constants
from ecs.components.component import Component
from ecs.components.transform_3d import Transform3D
from ecs.components.mesh import Mesh
from ecs.components.material import Material
from ecs.components.renderable import Renderable
from ecs.components.camera import Camera
from ecs.components.input_control import InputControl
from ecs.components.text_2d import Text2D


class Entity:

    def __init__(self, name=""):
        self.name = name
        self.sub_components = []
        self.is_subcomponent = False


class ComponentPool:

    COMPONENT_CLASS_MAP = {
        constants.COMPONENT_TYPE_TRANSFORM_3D: Transform3D,
        constants.COMPONENT_TYPE_MESH: Mesh,
        constants.COMPONENT_TYPE_RENDERABLE: Renderable,
        constants.COMPONENT_TYPE_CAMERA: Camera,
        constants.COMPONENT_TYPE_MATERIAL: Material,
        constants.COMPONENT_TYPE_INPUT_CONTROL: InputControl,
        constants.COMPONENT_TYPE_TEXT_2D: Text2D
    }

    def __init__(self):

        self.entity_uid_counter = 2  # TODO: We start from 2 to make it easy to discern the background [0, 1]

        # For holding states!
        self.entities = {}

        # Components
        self.transform_3d_components = {}
        self.transform_2d_components = {}
        self.camera_components = {}
        self.mesh_components = {}
        self.renderable_components = {}
        self.material_components = {}
        self.input_control_components = {}
        self.text_2d_components = {}
        self.directional_light_components = {}
        self.spot_light_components = {}
        self.point_light_components = {}

        self.component_storage_map = {
            constants.COMPONENT_TYPE_TRANSFORM_3D: self.transform_3d_components,
            constants.COMPONENT_TYPE_TRANSFORM_2D: self.transform_2d_components,
            constants.COMPONENT_TYPE_MESH: self.mesh_components,
            constants.COMPONENT_TYPE_RENDERABLE: self.renderable_components,
            constants.COMPONENT_TYPE_CAMERA: self.camera_components,
            constants.COMPONENT_TYPE_MATERIAL: self.material_components,
            constants.COMPONENT_TYPE_INPUT_CONTROL: self.input_control_components,
            constants.COMPONENT_TYPE_TEXT_2D: self.text_2d_components,
            constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: self.directional_light_components,
            constants.COMPONENT_TYPE_SPOT_LIGHT: self.spot_light_components,
            constants.COMPONENT_TYPE_POINT_LIGHT: self.point_light_components,
        }

    def create_entity(self, name="") -> int:
        uid = self.entity_uid_counter
        self.entities[uid] = Entity(name=name)
        self.entity_uid_counter += 1
        return uid

    def add_component(self, entity_uid: int, component_type: int, **kwargs):
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise TypeError(f"[ERROR] Component type '{component_type}' not supported")
        if entity_uid in component_pool:
            raise TypeError(f"[ERROR] Component type '{component_type}' already exists in component pool")

        component_pool[entity_uid] = ComponentPool.COMPONENT_CLASS_MAP[component_type](**kwargs)
        return component_pool[entity_uid]

    def remove_component(self, entity_uid: int, component_type: str):

        if self.entities[entity_uid].is_subcomponent:
            raise Exception("[ERROR] Tried to remove sub-component directly")
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            return

        component_pool[entity_uid].release()
        component_pool.pop(entity_uid)

    def get_component(self, entity_uid: int, component_type: str) -> Component:
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise TypeError(f"[ERROR] Component type '{component_type}' not supported")

        return component_pool.get(entity_uid, None)

    def get_all_components(self, entity_uid: int) -> list:
        components = []
        for _, storage in self.component_storage_map.items():
            if entity_uid in storage:
                components.append(storage[entity_uid])
        return components

    def get_entities_using_component(self, component_type: int) -> list:
        return list(self.component_storage_map[component_type].keys())


