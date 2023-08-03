from ecs.component import Component

class Entity:

    def __init__(self, name: str):
        self.name = name
        self.components = dict()

        
