

class Entity:

    def __init__(self, archetype: str):
        self.archetype = archetype

        # Components
        self.comp_transform = None
        self.comp_material = None
        self.comp_mesh = None

    def release(self):

        # Go over every component (that starts with "comp_") and release it if not None
        for attr_name in dir(self):
            if not attr_name.startswith("comp_"):
                continue

            component = getattr(self, attr_name)
            if component is not None and hasattr(component, 'release'):
                component.release()
