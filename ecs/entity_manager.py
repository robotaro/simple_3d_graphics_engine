class Entity:

    def __init__(self, name: str):
        self.name = name
        self.components = dict()


class EntityManager:

    def __init__(self):
        pass

    def add_component(self, entity_id: str, component_type: str):
        pass
