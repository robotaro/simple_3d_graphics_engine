import glm
from src.core import constants


class TransformComponent:

    _type = "transform_3d"

    __slots__ = [
        "local_matrix",
        "world_matrix",
        "inverse_world_matrix",
        "position",
        "rotation",
        "scale",
        "use_degrees",
        "input_values_updated",
        "local_matrix_updated",
        "dirty"
    ]

    def __init__(self, position: tuple, rotation: tuple, scale: tuple, use_degrees=False):

        self.position = glm.vec3(position)
        self.rotation = glm.vec3(rotation)
        self.scale = glm.vec3(scale)

        if len(self.scale) == 1:
            self.scale = glm.vec3(self.scale[0], self.scale[0], self.scale[0])

        if len(self.scale) == 2:
            raise Exception("[ERROR] Input scale from parameters contains 2 values. Please make sure you have"
                            "either 1 or 3")

        self.use_degrees = use_degrees

        if self.use_degrees:
            self.rotation = glm.radians(self.rotation)

        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)
        self.inverse_world_matrix = glm.mat4(1.0)
        self.input_values_updated = True
        self.local_matrix_updated = False
        self.dirty = True

    def update(self) -> bool:
        if self.local_matrix_updated:
            self.position = glm.vec3(self.local_matrix[3])
            self.rotation = glm.eulerAngles(self.local_matrix)
            # TODO: Scale is missing!!!
            self.local_matrix_updated = False
            self.input_values_updated = False
            self.dirty = True
            return True

        if self.input_values_updated:
            self.local_matrix = glm.translate(glm.mat4(1.0), self.position) * \
                                glm.mat4_cast(glm.quat(self.rotation)) * \
                                glm.scale(glm.mat4(1.0), self.scale)
            self.input_values_updated = False
            self.dirty = True
            return True

        return False

    def move(self, delta_position: glm.vec3):
        self.position += delta_position
        self.input_values_updated = True

    def rotate(self, delta_rotation: glm.vec3):
        self.rotation += delta_rotation
        self.input_values_updated = True

    def set_position(self, position: tuple):
        self.position = glm.vec3(position)
        self.input_values_updated = True

    def set_rotation(self, rotation: tuple):
        self.rotation = glm.vec3(rotation)
        self.input_values_updated = True

    def render_ui(self, imgui):
        imgui.text("Transform")
        a, self.position = imgui.drag_float3("Position", *self.position, constants.IMGUI_DRAG_FLOAT_PRECISION)
        b, self.rotation = imgui.drag_float3("Rotation", *self.rotation, constants.IMGUI_DRAG_FLOAT_PRECISION)
        c, self.scale = imgui.drag_float3("Scale", *self.scale, constants.IMGUI_DRAG_FLOAT_PRECISION)
        self.input_values_updated |= a | b | c
        imgui.spacing()