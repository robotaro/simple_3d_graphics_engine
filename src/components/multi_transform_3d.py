import numpy as np
import moderngl


from src.core import constants
from src.core.component import Component


class MultiTransform3D(Component):

    _type = "transform"

    __slots__ = [
        "world_matrices",
        "dirty"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)
        self.world_matrices = None
        self.dirty = True

    def initialise(self, **kwargs):

        data_manager = kwargs[constants.MODULE_NAME_DATA_MANAGER]
        resource_id = self.parameters.get(constants.COMPONENT_ARG_RESOURCE_ID, None)

        if resource_id is None:
            return

        self.world_matrices = data_manager.data_groups[resource_id]
        self.dirty = True

    def update_ubo(self, ubo: moderngl.UniformBlock):

        if not self.dirty:
            return

        # Write the data to the UBO
        ubo.write(self.world_matrices.tobytes(), offset=0)
        self.dirty = False

    def get_num_transforms(self) -> int:
        if self.world_matrices is None:
            return None

        return self.world_matrices.shape[0]
