import numpy as np
import logging
from typing import Union

from src.core import constants
from src.core.entity import Entity
from src.core.component import Component
from src.components.transform_3d import Transform3D
from src.components.collider import Collider
from src.components.mesh import Mesh
from src.components.material import Material
from src.components.camera import Camera
from src.components.input_control import InputControl
from src.components.overlay_2d import Overlay2D
from src.components.point_light import PointLight
from src.components.directional_light import DirectionalLight
from src.components.gizmo_3d import Gizmo3D
from src.components.robot import Robot
from src.components.debug_mesh import DebugMesh
from src.components.skeleton import Skeleton

MAX_POINT_LIGHTS = 8


class Scene:

    COMPONENT_CLASS_MAP = {
        constants.COMPONENT_TYPE_TRANSFORM_3D: Transform3D,
        constants.COMPONENT_TYPE_MESH: Mesh,
        constants.COMPONENT_TYPE_CAMERA: Camera,
        constants.COMPONENT_TYPE_MATERIAL: Material,
        constants.COMPONENT_TYPE_INPUT_CONTROL: InputControl,
        constants.COMPONENT_TYPE_OVERLAY_2D: Overlay2D,
        constants.COMPONENT_TYPE_POINT_LIGHT: PointLight,
        constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: DirectionalLight,
        constants.COMPONENT_TYPE_COLLIDER: Collider,
        constants.COMPONENT_TYPE_GIZMO_3D: Gizmo3D,
        constants.COMPONENT_TYPE_ROBOT: Robot,
        constants.COMPONENT_TYPE_DEBUG_MESH: DebugMesh,
        constants.COMPONENT_TYPE_SKELETON: Skeleton,
    }

    COMPONENT_NAME_MAP = {
        "transform_3d": constants.COMPONENT_TYPE_TRANSFORM_3D,
        "mesh": constants.COMPONENT_TYPE_MESH,
        "camera": constants.COMPONENT_TYPE_CAMERA,
        "material": constants.COMPONENT_TYPE_MATERIAL,
        "input_control": constants.COMPONENT_TYPE_INPUT_CONTROL,
        "overlay_2d": constants.COMPONENT_TYPE_OVERLAY_2D,
        "directional_light": constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT,
        "spot_light": constants.COMPONENT_TYPE_SPOT_LIGHT,
        "point_light": constants.COMPONENT_TYPE_POINT_LIGHT,
        "collider": constants.COMPONENT_TYPE_COLLIDER,
        "gizmo_3d": constants.COMPONENT_TYPE_GIZMO_3D,
        "robot": constants.COMPONENT_TYPE_ROBOT,
        "debug_mesh": constants.COMPONENT_TYPE_DEBUG_MESH,
        "skeleton": constants.COMPONENT_TYPE_SKELETON
    }

    __slots__ = [
        "logger",
        "entity_uid_counter",
        "entities",
        "component_master_pool",
        "available_point_light_indices",
        "available_directional_light_indices",
        "available_material_indices",
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger

        # TODO: We start from 2 to make it easy to discern the background [0, 1]
        self.entity_uid_counter = constants.COMPONENT_POOL_STARTING_ID_COUNTER
        self.entities = {}
        self.component_master_pool = {component_type: {} for component_type, _ in Scene.COMPONENT_CLASS_MAP.items()}

        self.available_material_indices = [i for i in reversed(range(constants.SCENE_MAX_NUM_MATERIALS))]
        self.available_point_light_indices = [i for i in reversed(range(constants.SCENE_MAX_NUM_POINT_LIGHTS))]
        self.available_directional_light_indices = [i for i in reversed(range(constants.SCENE_MAX_NUM_DIRECTIONAL_LIGHTS))]

    def add_entity(self, entity_blueprint: dict, parent_entity_uid=None, system_owned=False) -> int:

        entity_name = entity_blueprint.get("name", "unamed_entity")
        entity_uid = self._create_entity(name=entity_name, parent_uid=parent_entity_uid, system_owned=system_owned)

        # Add children first, if any
        if "entity" in entity_blueprint:
            for sub_entity_blueprint in entity_blueprint["entity"]:

                # Recursively go into child's blueprint to create it
                child_uid = self.add_entity(entity_blueprint=sub_entity_blueprint,
                                            parent_entity_uid=entity_uid,
                                            system_owned=system_owned)

                # And once you are back, add this child to its parent
                self.entities[entity_uid].children_uids.append(child_uid)

        # And add components after
        for component in entity_blueprint["components"]:

            component_type = Scene.COMPONENT_NAME_MAP.get(component["name"], None)
            if component_type is None:
                self.logger.error(f"Component {component['name']} is not supported.")
                continue

            self.add_component(entity_uid=entity_uid,
                               component_type=component_type,
                               parameters=component["parameters"],
                               system_owned=system_owned)

        return entity_uid

    def add_component(self, entity_uid: int, component_type: int, parameters: dict, system_owned=False):
        component_pool = self.component_master_pool.get(component_type, None)

        # TODO: This should expanded to all components that will be uploaded to the UBOs
        if component_type == constants.COMPONENT_TYPE_MATERIAL:
            parameters["ubo_index"] = self.available_material_indices.pop()

        if component_type == constants.COMPONENT_TYPE_POINT_LIGHT:
            parameters["ubo_index"] = self.available_point_light_indices.pop()

        if component_type == constants.COMPONENT_TYPE_POINT_LIGHT:
            parameters["ubo_index"] = self.available_point_light_indices.pop()

        # Safety
        if component_pool is None:
            raise KeyError(f"[ERROR] Component type '{component_type}' not supported")
        if entity_uid in component_pool:
            raise KeyError(f"[ERROR] Component type '{component_type}' already exists in component pool")

        component_pool[entity_uid] = Scene.COMPONENT_CLASS_MAP[component_type](parameters=parameters,
                                                                               system_owned=system_owned)
        return component_pool[entity_uid]

    def remove_component(self, entity_uid: int, component_type: int) -> bool:

        if self.entities[entity_uid].has_parent:
            self.logger.warning(f"ComponentPool | remove_component() | Entity {entity_uid} has a parent")
            return False

        component_pool = self.component_master_pool.get(component_type, None)

        # TODO: This should expanded to all components that will be uploaded to the UBOs
        if component_type == constants.COMPONENT_TYPE_MATERIAL:
            self.available_material_indices.append(component_pool[entity_uid].ubo_index)

        # Safety
        if component_pool is None:
            self.logger.warning(f"ComponentPool | remove_component() | Component type {component_type} is not supported")
            return False

        component_pool[entity_uid].release()
        component_pool.pop(entity_uid)
        return True

    def get_entity(self, entity_uid: int) -> Union[Entity, None]:

        entity = self.entities.get(entity_uid, None)
        if entity is None:
            raise KeyError(f"[ERROR] Entity ID '{entity}' not present")

        return entity

    def get_component(self, entity_uid: int, component_type: int) -> Union[Component, None]:

        entity = self.entities.get(entity_uid, None)
        if entity is None:
            raise KeyError(f"[ERROR] Entity ID '{entity}' not present")

        component_pool = self.component_master_pool.get(component_type, None)
        if component_pool is None:
            raise KeyError(f"[ERROR] Component '{component_type}' not present")

        if entity_uid in component_pool:
            return component_pool[entity_uid]

        if entity.has_parent:
            return self.get_component(entity_uid=entity.parent_uid, component_type=component_type)

        return None

    def get_all_sub_entity_components(self, parent_entity_uid: int, component_type: int) -> list:

        def get_components_recursively(entity_uid: int, component_type: int, output_list: list):

            # Add selected component type to output if present in this entity
            pool = self.component_master_pool[component_type]
            if entity_uid in pool:
                output_list.append(pool[entity_uid])

            # And go recursivelly through its children
            entity = self.entities[entity_uid]
            for child_uid in entity.children_uids:
                get_components_recursively(entity_uid=child_uid,
                                            component_type=component_type,
                                            output_list=output_list)

        parent_entity = self.entities.get(parent_entity_uid, None)
        output_components = []
        get_components_recursively(entity_uid=parent_entity_uid,
                                    component_type=component_type,
                                    output_list=output_components)

        return output_components

    def get_pool(self, component_type: int) -> dict:
        return self.component_master_pool.get(component_type, None)

    def get_all_entity_uids(self, component_type: int) -> list:
        return list(self.component_master_pool[component_type].keys())

    def get_children_uids(self, entity_uid: int) -> []:

        entity = self.entities.get(entity_uid, None)
        if entity is None:
            raise KeyError(f"[ERROR] Entity ID '{entity}' not present")

        return self.entities[entity_uid].children_uids

    def get_all_components(self, entity_uid: int) -> list:
        return [storage[entity_uid] for _, storage in self.component_master_pool.items() if entity_uid in storage]

    def get_entities_using_component(self, component_type: int) -> list:
        return list(self.component_master_pool[component_type].keys())

    def _create_entity(self, name="", parent_uid=None, system_owned=False) -> int:
        uid = self.entity_uid_counter
        self.entities[uid] = Entity(name=name, parent=parent_uid, system_owned=system_owned)
        self.entity_uid_counter += 1
        return uid
