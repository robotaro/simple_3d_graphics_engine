import moderngl

from src3.entities.entity import Entity


class EntityFactory:

    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

    def create_renderable(self, component_list: list):
        entity = Entity(archetype="renderable", component_list=component_list)
        return entity
