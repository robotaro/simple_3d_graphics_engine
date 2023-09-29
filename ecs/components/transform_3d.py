import numpy as np
from ecs.math import mat4
from ecs.math import mat3
from ecs import constants

from ecs.components.component import Component


class Transform3D(Component):

    _type = "transform"

    __slots__ = [
        "world_matrix",
        "local_matrix",
        "position",
        "rotation",
        "look_at_target",
        "scale"
    ]

    def __init__(self, **kwargs):
        super().__init__()

        self.world_matrix = np.eye(4, dtype=np.float32)
        self.local_matrix = np.eye(4, dtype=np.float32)

        self.position = tuple(kwargs.get("position", [0.0, 0.0, 0.0]))
        self.rotation = tuple(kwargs.get("rotation", [0.0, 0.0, 0.0]))

        self.look_at_target = kwargs.get("look_at_target", None)
        if self.look_at_target is not None:
            self.look_at_target = np.array(self.look_at_target, dtype=np.float32)

        self.scale = kwargs.get("scale", 1.0)

    def update(self):

        if self.look_at_target is not None:

            # TODO: Optimise this! Too many conversions during update!
            #       But this is to leave position and rotation as tuples for the imgui... sigh
            self.local_matrix = mat4.look_at(
                position=np.array(self.position, dtype=np.float32),
                target=self.look_at_target,
                up=constants.TRANSFORMS_UP_VECTOR)
            return

        # TODO: Add the _dirty_flag check to avoid unecessary updates
        self.local_matrix = mat4.compute_transform(position=self.position,
                                                   rotation_rad=self.rotation,
                                                   scale=self.scale)
