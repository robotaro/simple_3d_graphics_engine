import logging

from ecs import constants
from ecs.components.component import Component
from ecs.components.transform_3d import Transform3D
from ecs.components.collider import Collider
from ecs.components.mesh import Mesh
from ecs.components.material import Material
from ecs.components.camera import Camera
from ecs.components.input_control import InputControl
from ecs.components.text_2d import Text2D
from ecs.components.point_light import PointLight
from ecs.components.directional_light import DirectionalLight


class Entity:

    __slots__ = [
        "name",
        "parent_entity",
        "children_entities"
    ]

    def __init__(self, name="", parent=None):
        self.name = name
        self.parent_entity = parent
        self.children_entities = []

    @property
    def has_parent(self):
        return self.parent_entity is not None


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
        }

        # This variable is a temporary solution to keep track of all entities added during the xml scene loading
        self.entity_uids_to_be_initiliased = []

    def add_entity(self, entity_blueprint: dict, parent_entity_uid=None) -> None:

        entity_name = entity_blueprint.get("name", "unamed_entity")
        entity_uid = self._create_entity(name=entity_name, parent_uid=parent_entity_uid)

        if "entity" in entity_blueprint:
            for sub_entity_blueprint in entity_blueprint["entity"]:
                self.add_entity(entity_blueprint=sub_entity_blueprint, parent_entity_uid=entity_uid)

        self.entity_uids_to_be_initiliased.append(entity_uid)

        for component in entity_blueprint["components"]:

            component_type = constants.COMPONENT_MAP.get(component["name"], None)
            if component_type is None:
                self.logger.error(f"Component {component['name']} is not supported.")
                continue

            self.add_component(entity_uid=entity_uid,
                               component_type=component_type,
                               parameters=component["parameters"])

    def add_component(self, entity_uid: int, component_type: int, parameters: dict):
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            raise TypeError(f"[ERROR] Component type '{component_type}' not supported")
        if entity_uid in component_pool:
            raise TypeError(f"[ERROR] Component type '{component_type}' already exists in component pool")

        component_pool[entity_uid] = ComponentPool.COMPONENT_CLASS_MAP[component_type](parameters=parameters)
        return component_pool[entity_uid]

    def remove_component(self, entity_uid: int, component_type: str):

        if self.entities[entity_uid].has_parent:
            raise Exception("[ERROR] Tried to remove sub-component directly")
        component_pool = self.component_storage_map.get(component_type, None)

        # Safety
        if component_pool is None:
            return

        component_pool[entity_uid].release()
        component_pool.pop(entity_uid)

    def get_component(self, entity_uid: int, component_type: str) -> Component:

        entity = self.entities.get(entity_uid, None)
        if entity is None:
            raise TypeError(f"[ERROR] Entity ID '{entity}' not present")

        component_pool = self.component_storage_map.get(component_type, None)

        component = component_pool.get(entity_uid, None)
        if component is not None:
            return component

        if entity.has_parent:
            return self.get_component(entity_uid=entity_uid.parent_entity)

        raise TypeError(f"[ERROR] Component type '{component_type}' not supported")

    def get_all_components(self, entity_uid: int) -> list:
        return [storage[entity_uid] for _, storage in self.component_storage_map.items() if entity_uid in storage]

    def get_entities_using_component(self, component_type: int) -> list:
        return list(self.component_storage_map[component_type].keys())

    def _create_entity(self, name="", parent_uid=None) -> int:
        uid = self.entity_uid_counter
        self.entities[uid] = Entity(name=name, parent=parent_uid)
        self.entity_uid_counter += 1
        return uid
