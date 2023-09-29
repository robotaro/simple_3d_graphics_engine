import moderngl


class Component:

    _type = "base_component"

    __slots__ = [
        "initialised"
    ]

    def __init__(self):
        self.initialised = False

    def initialise(self, **kwargs):
        pass

    def release(self):
        pass
