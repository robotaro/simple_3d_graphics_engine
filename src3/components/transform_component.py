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
        "dirty",
        "parent",
        "children"
    ]

    def __init__(self, position: glm.vec3, rotation: glm.vec4, scale: glm.vec3, use_degrees=False):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent = None
        self.children = []

        self.use_degrees = use_degrees

        if self.use_degrees:
            self.rotation = glm.radians(self.rotation)

        self.local_matrix = glm.translate(glm.mat4(1.0), self.position) * \
                            glm.mat4_cast(self.rotation) * \
                            glm.scale(glm.mat4(1.0), self.scale)

        self.world_matrix = glm.mat4(1.0)
        self.inverse_world_matrix = glm.mat4(1.0)
        self.input_values_updated = True
        self.local_matrix_updated = False
        self.dirty = True

    def update_world_matrix(self) -> bool:
        if self.local_matrix_updated:
            self.position, self.rotation, self.scale = self.decompose_matrix(matrix=self.local_matrix)

            self.local_matrix_updated = False
            self.input_values_updated = False
            self.dirty = True

        if self.input_values_updated:
            self.local_matrix = glm.translate(glm.mat4(1.0), self.position) * \
                                glm.mat4_cast(self.rotation) * \
                                glm.scale(glm.mat4(1.0), self.scale)
            self.input_values_updated = False
            self.dirty = True

        # Update world matrix based on parent's world matrix
        if self.parent:
            self.world_matrix = self.parent.world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix

        # Recursively update children's world matrices
        for child in self.children:
            child.update_world_matrix()

        return True

    def decompose_matrix(self, matrix: glm.mat4):
        # Extract translation
        position = glm.vec3(matrix[3])

        # Extract scale
        scale = glm.vec3(glm.length(matrix[0]), glm.length(matrix[1]), glm.length(matrix[2]))

        # Remove the scaling from the matrix
        rotation_matrix = glm.mat4(matrix)
        rotation_matrix[0] /= scale.x
        rotation_matrix[1] /= scale.y
        rotation_matrix[2] /= scale.z

        # Extract rotation (quaternion)
        rotation_quat = glm.quat_cast(rotation_matrix)
        rotation_euler = glm.degrees(glm.eulerAngles(rotation_quat))

        return position, rotation_euler, scale

    def move(self, delta_position: glm.vec3):
        self.position += delta_position
        self.input_values_updated = True

    def rotate(self, delta_rotation: glm.vec3):
        self.rotation += delta_rotation
        self.input_values_updated = True

    def set_position(self, position: glm.vec3):
        self.position = position
        self.input_values_updated = True

    def set_rotation(self, rotation: glm.vec3):
        self.rotation = rotation
        self.input_values_updated = True

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def render_ui(self, imgui):
        imgui.text("Transform")
        a, self.position = imgui.drag_float3("Position", *self.position, constants.IMGUI_DRAG_FLOAT_PRECISION)
        b, self.rotation = imgui.drag_float3("Rotation", *self.rotation, constants.IMGUI_DRAG_FLOAT_PRECISION)
        c, self.scale = imgui.drag_float3("Scale", *self.scale, constants.IMGUI_DRAG_FLOAT_PRECISION)
        self.input_values_updated |= a | b | c
        imgui.spacing()
