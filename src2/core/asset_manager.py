

class AssetManager:

    __slots__ = [
        "visible",
        "entities"
    ]

    def __init__(self):
        self.visible = True
        self.entities = {}

    def __getitem__(self, entity_id):
        return self.entities[entity_id]
