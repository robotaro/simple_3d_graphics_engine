from typing import Union


class Entity:

    def __init__(self, uid: Union[int, str], name=""):
        self.uid = uid
        self.name = name
        self.components = {}


class EntityManager:

    def __init__(self):
        pass

    def add_component(self, entity_id: str, component_type: str):
        pass
