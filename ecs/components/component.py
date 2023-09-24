import moderngl


class Component:

    _type = "base_component"

    __slots__ = [
        "gpu_initialised"
    ]

    def __init__(self):
        self.gpu_initialised = False

    def initialise_on_gpu(self, ctx: moderngl.Context) -> None:
        pass
    
    def release(self):
        pass