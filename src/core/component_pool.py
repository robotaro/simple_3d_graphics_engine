import logging
from typing import Union

from src.core import constants
from src.components.component import Component
from src.components.transform_3d import Transform3D
from src.components.collider import Collider
from src.components.mesh import Mesh
from src.components.material import Material
from src.components.camera import Camera
from src.components.input_control import InputControl
from src.components.text_2d import Text2D
from src.components.point_light import PointLight
from src.components.directional_light import DirectionalLight
from src.components.gizmo_3d import Gizmo3D
from src.components.robot import Robot
from src.components.debug_mesh import DebugMesh


class Entity:

    __slots__ = [
        "name",
        "root_parent_uid",
        "parent_uid",
        "children_uids",
        "system_owned"
    ]

    def __init__(self, name="", parent=None, system_owned=False):
        self.name = name
        self.root_parent_uid = None  # TODO: This should be filled during initialisation, or when the entity tree is modified
        self.parent_uid = parent
        self.children_uids = []
        self.system_owned = system_owned

    @property
    def has_parent(self):
        return self.parent_uid is not None


class ComponentPool:

    COMPONENT_CLASS_MAP = {
        constants.COMPONENT_TYPE_TRANSFORM_3D: Transform3D,
        constants.COMPONENT_TYPE_MESH: Mesh,
        constants.COMPONENT_TYPE_CAMERA: Camera,
        constants.COMPONENT_TYPE_MATERIAL: Material,
        constants.COMPONENT_TYPE_INPUT_CONTROL: InputControl,
        constants.COMPONENT_TYPE_TEXT_2D: Text2D,
        constants.COMPONENT_TYPE_POINT_LIGHT: PointLight,
        constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: DirectionalLight,
        constants.COMPONENT_TYPE_COLLIDER: Collider,
        constants.COMPONENT_TYPE_GIZMO_3D: Gizmo3D,
        constants.COMPONENT_TYPE_ROBOT: Robot,
        constants.COMPONENT_TYPE_DEBUG_MESH: DebugMesh,
    }

    COMPONENT_NAME_MAP = {
        "transform_3d": constants.COMPONENT_TYPE_TRANSFORM_3D,
        "mesh": constants.COMPONENT_TYPE_MESH,
        "camera": constants.COMPONENT_TYPE_CAMERA,
        "material": constants.COMPONENT_TYPE_MATERIAL,
        "input_control": constants.COMPONENT_TYPE_INPUT_CONTROL,
        "text_2d": constants.COMPONENT_TYPE_TEXT_2D,
        "directional_light": constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT,
        "spot_light": constants.COMPONENT_TYPE_SPOT_LIGHT,
        "point_light": constants.COMPONENT_TYPE_POINT_LIGHT,
        "collider": constants.COMPONENT_TYPE_COLLIDER,
        "gizmo_3d": constants.COMPONENT_TYPE_GIZMO_3D,
        "robot": constants.COMPONENT_TYPE_ROBOT,
        "debug_mesh": constants.COMPONENT_TYPE_DEBUG_MESH
    }

    def __init__(self, logger: logging.Logger):

        self.logger = logger

        # TODO: We start from 2 to make it easy to discern the background [0, 1]
        self.entity_uid_counter = constants.COMPONENT_POOL_STARTING_ID_COUNTER

        # For holding states!
        self.entities = {}

        # Components
        self.transform_3d_components = {}
        self.transform_2d_components = {}
        self.camera_components = {}
        self.mesh_components = {}
        self.material_components = {}
        self.input_control_components = {}
        self.text_2d_components = {}
        self.directional_light_components = {}
        self.spot_light_components = {}
        self.point_light_components = {}
        self.collider_components = {}
        self.gizmo_3d_components = {}
        self.robot_components = {}
        self.debug_mesh_components = {}

        self.component_storage_map = {
            constants.COMPONENT_TYPE_TRANSFORM_3D: self.transform_3d_components,
            constants.COMPONENT_TYPE_TRANSFORM_2D: self.transform_2d_components,
            constants.COMPONENT_TYPE_MESH: self.mesh_components,
            constants.COMPONENT_TYPE_CAMERA: self.camera_components,
            constants.COMPONENT_TYPE_MATERIAL: self.material_components,
            constants.COMPONENT_TYPE_INPUT_CONTROL: self.input_control_components,
            constants.COMPONENT_TYPE_TEXT_2D: self.text_2d_components,
            constants.COMPONENT_TYPE_DIRECTIONAL_LIGHT: self.directional_light_components,
            constants.COMPONENT_TYPE_SPOT_LIGHT: self.spot_light_components,
            constants.COMPONENT_TYPE_POINT_LIGHT: self.point_light_components,
            constants.COMPONENT_TYPE_COLLIDER: self.collider_components,
            constants.COMPONENT_TYPE_GIZMO_3D: self.gizmo_3d_components,
            constants.COMPONENT_TYPE_ROBOT: self.robot_components,
            constants.COMPONENT_TYPE_DEBUG_MESH: self.debug_mesh_components,
        }

        # This variable is a temporary solution to keep track of all entities added during the xml scene loading
        self.entity_uids_to_be_initiliased = []

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

        self.entity_uids_to_be_initiliased.append(entity_uid)

        # And add components after
        for component in entity_blueprint["components"]:

            component_type = ComponentPool.COMPONENT_NAME_MAP.get(component["name"], None)
            if component_type is None:
                self.logger.error(f"Component {component['name']} is not supported.")
                continue

            self.add_component(entity_uid=entity_uid,
                               component_type=component_type,
                               parameters=component["parameters"],
                               system_owned=system_owned)

        return entity_uid

    def add_component(self, entity_uid: int, component_type: int, parameters: dict, system_owned=False):
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise KeyError(f"[ERROR] Component type '{component_type}' not supported")
        if entity_uid in component_pool:
            raise KeyError(f"[ERROR] Component type '{component_type}' already exists in component pool")

        component_pool[entity_uid] = ComponentPool.COMPONENT_CLASS_MAP[component_type](parameters=parameters,
                                                                                       system_owned=system_owned)
        return component_pool[entity_uid]

    def remove_component(self, entity_uid: int, component_type: int) -> bool:

        if self.entities[entity_uid].has_parent:
            self.logger.warning(f"ComponentPool | remove_component() | Entity {entity_uid} has a parent")
            return False

        component_pool = self.component_storage_map.get(component_type, None)

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

        selected_component_pool = self.component_storage_map[component_type]

        if entity_uid in selected_component_pool:
            return selected_component_pool[entity_uid]

        if entity.has_parent:
            return self.get_component(entity_uid=entity.parent_uid, component_type=component_type)

        return None

    def get_children_uids(self, entity_uid: int) -> []:

        entity = self.entities.get(entity_uid, None)
        if entity is None:
            raise KeyError(f"[ERROR] Entity ID '{entity}' not present")

        return self.entities[entity_uid].children_uids

    def get_all_components(self, entity_uid: int) -> list:
        return [storage[entity_uid] for _, storage in self.component_storage_map.items() if entity_uid in storage]

    def get_entities_using_component(self, component_type: int) -> list:
        return list(self.component_storage_map[component_type].keys())

    def _create_entity(self, name="", parent_uid=None, system_owned=False) -> int:
        uid = self.entity_uid_counter
        self.entities[uid] = Entity(name=name, parent=parent_uid, system_owned=system_owned)
        self.entity_uid_counter += 1
        return uid
