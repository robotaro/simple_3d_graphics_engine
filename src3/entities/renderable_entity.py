
from src3.entities.entity import Entity


class RenderableEntity(Entity):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, program_name: str):
        # Set model transform

        # Render VAO
        pass