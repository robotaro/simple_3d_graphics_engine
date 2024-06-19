import numpy as np


class EntityFactory:

    def __init__(self):
        pass

    def create_entity(self, archetype: str, components: list):
        entity = Entity(archetype)

        # Map archetypes to required component classes
        archetype_requirements = {
            "basic_entity": [TransformComponent, MaterialComponent],
            "complex_entity": [TransformComponent, MaterialComponent, MeshComponent]
        }

        if archetype not in archetype_requirements:
            raise ValueError(f"Unknown archetype: {archetype}")

        required_components = archetype_requirements[archetype]

        for component_class in required_components:
            for component in components:
                if isinstance(component, component_class):
                    attr_name = f"comp_{component_class.__name__.replace('Component', '').lower()}"
                    setattr(entity, attr_name, component)
                    break
            else:
                raise ValueError(f"Missing required component: {component_class.__name__}")

        return entity

    def create_mesh(self, vertices: np.):