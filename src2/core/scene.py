import os
from typing import Tuple, Dict, Optional

import moderngl

from src.core import constants
from src2.core.shader_program_library import ShaderProgramLibrary
from logging import Logger

# Entities
from src2.entities.entity import Entity
from src2.entities.camera import Camera
from src2.entities.point_light import PointLight
from src2.entities.directional_light import DirectionalLight

# Component
from src2.components.transform import Transform
from src2.components.material import Material
from src2.components.mesh import Mesh


class Scene:

    def __init__(self,
                 logger: Logger,
                 shader_library: ShaderProgramLibrary,
                 ctx: moderngl.Context,
                 name: Optional[str] = None,
                 params: Optional[Dict] = None):

        self.name = name
        self.params = params if params else {}
        self.ctx = ctx
        self.shader_library = shader_library
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
        self.register_entity_type(name="point_light", entity_class=PointLight)
        self.register_entity_type(name="directional_light", entity_class=DirectionalLight)

        # Register components
        self.register_component_type(name="mesh", component_clas=Mesh)
        self.register_component_type(name="transform", component_clas=Transform)
        self.register_component_type(name="material", component_clas=Material)

    def register_entity_type(self, name: str, entity_class):
        if name in self.registered_entity_types:
            raise KeyError(f"[ERROR] Entity type {name} already registered")
        self.registered_entity_types[name] = entity_class

    def register_component_type(self, name: str, component_clas):
        if name in self.registered_component_types:
            raise KeyError(f"[ERROR] Component type {name} already registered")
        self.registered_component_types[name] = component_clas

    def create_entity(self, entity_type: str, name: str, params: str, components: dict) -> int:

        """

        :param entity_type:
        :param name:
        :param params:
        :param components: dict, lists of component parameters per type stored in this dictionary
        :return:
        """

        # Generate new unique id fo r
        entity_id = self.available_entity_ids.pop()

        new_entity = self.registered_entity_types[entity_type](name=name, params=params)
        if isinstance(new_entity, Camera):
            self.cameras[entity_id] = new_entity
        else:
            self.entities[entity_id] = new_entity

        # Add components
        for component_type, component_params in components.items():

            # Use a pre-existing shared component
            if "shared_ref" in component_params:
                if "shared_ref" not in self.shared_components:
                    raise KeyError(f"[ERROR] Shared component {component_params['shared_ref']} referenced in "
                                   f"entity does not exit ")
                new_entity.components[component_type] = self.shared_components[component_params["shared_ref"]]
                continue

            # Or create a brand new one
            new_entity.components[component_type] = self.registered_component_types[component_type](
                params=component_params)

        return entity_id

    def destroy_entity(self, entity_id: int):
        pass

    def create_shared_component(self, shared_ref: str, component_type: str, params: str) -> int:
        self.shared_components[shared_ref] = self.registered_component_types[component_type](
            name=shared_ref,
            params=params)

    def render(self):

        # Setup lights

        # Render meshes per camera
        for _, camera in self.cameras.items():
            program["projection_matrix"].write(camera_component.get_projection_matrix().T.tobytes())
            program["view_matrix"].write(camera_transform.inverse_world_matrix.T.tobytes())

            # Render Opaque Entities
            transparent_entities = []
            for _, entity in self.entities.items():
                entity.render()

            # TODO: Sort transparent entities according to their distance relative to the camera

            # Render Transparent Enties
            for entity in transparent_entities:
                entity.render()


    def destroy(self):
        pass
