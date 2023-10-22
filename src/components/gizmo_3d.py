from src.components.component import Component


class Gizmo3D(Component):

    _type = "gizmo_3d"

    __slots__ = [
        "mode",
        "x_axis_entity_uid",
        "y_axis_entity_uid",
        "z_axis_entity_uid",
        "x_axis_collider_uid",
        "y_axis_collider_uid",
        "z_axis_collider_uid",
        "selected_axis",
        "active"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.mode = Component.dict2int(input_dict=parameters, key="mode", default_value=0)
        self.selected_axis = None

        self.x_axis_entity_uid = None
        self.y_axis_entity_uid = None
        self.z_axis_entity_uid = None

        self.x_axis_collider_uid = None
        self.y_axis_collider_uid = None
        self.z_axis_collider_uid = None

        self.active = False
