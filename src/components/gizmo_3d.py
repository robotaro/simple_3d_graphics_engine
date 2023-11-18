import numpy as np

from src.components.component import Component


class Gizmo3D(Component):

    _type = "gizmo_3d"

    __slots__ = [
        "mode",
        "axes_entities_uids",
        "selected_axis",
        "active",
        "exclusive_to_camera_uid"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.mode = Component.dict2int(input_dict=parameters, key="mode", default_value=0)
        self.axes_entities_uids = np.array([-1, -1, -1], dtype=np.int32)
