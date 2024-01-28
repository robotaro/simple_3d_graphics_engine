
class EntityGroup:

    __slots__ = [
        "name",
        "visible",
        "entities"
    ]

    def __init__(self, name: str):
        self.name = name
        self.visible = True
        self.entities = {}

    def __getitem__(self, entity_id):
        return self.entities[entity_id]
