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

        self.parent = None
        self.children = []

        self.position = position
        self.rotation = rotation
        self.scale = scale

        self.use_degrees = use_degrees

        if self.use_degrees:
            self.rotation = glm.radians(self.rotation)

        self.world_matrix = None  # Define before the local matrix
        self.local_matrix = None
        self.update_local_matrix(self._calculate_local_matrix())

        self.input_values_updated = True
        self.local_matrix_updated = False
        self.dirty = True

    def update_position(self, position: glm.vec3):
        self.position = position
        self.update_vectors()

    def update_rotation(self, rotation: glm.quat):
        self.rotation = rotation
        self.update_vectors()

    def update_scale(self, scale: glm.quat):
        self.scale = scale
        self.update_vectors()

    def update_vectors(self):

        # 1) Update local matrix from position, rotation (quat) and scale vectors
        self.local_matrix = self._calculate_local_matrix()

        # 2) Update world matrix from local matrix and parent matrix
        if self.parent:
            self.world_matrix = self.parent.world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix

        # 3) Update children
        for child in self.children:
            child.update_from_parent(self.world_matrix)

    def update_local_matrix(self, local_matrix: glm.mat4):

        # Replace current local matrix if a new one is provided
        if isinstance(local_matrix, glm.mat4):
            self.local_matrix = local_matrix

        # 1) Update vectors (position, rotation and scale) from local matrix
        self.position, self.rotation, self.scale = self.decompose_matrix(self.local_matrix)

        # 2) Update world matrix from local matrix and parent matrix
        if self.parent:
            self.world_matrix = self.parent.world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix

        # 3) Update children
        for child in self.children:
            child.update_from_parent(self.world_matrix)

    def update_world_matrix(self, world_matrix: glm.mat4):

        # Replace current world matrix if a new one is provided
        if isinstance(world_matrix, glm.mat4):
            self.world_matrix = world_matrix

        # 1) Update local matrix using the parent's world matrix if available
        if self.parent:
            self.local_matrix = glm.inverse(self.parent.world_matrix) * self.world_matrix
        else:
            self.local_matrix = self.world_matrix

        # 2) Update vectors (position, rotation and scale) from local matrix
        self.position, self.rotation, self.scale = self.decompose_matrix(self.local_matrix)

        # 3) Update children
        for child in self.children:
            child.update_from_parent(self.world_matrix)

    def update_from_parent(self, parent_world_matrix: glm.mat4):

        if parent_world_matrix is not None:
            self.world_matrix = parent_world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix

        # Update world matrix from local matrix and parent matrix
        self.world_matrix = parent_world_matrix * self.local_matrix

        # Recursively update children's world matrices
        for child in self.children:
            child.update_from_parent(self.world_matrix)

    def _calculate_local_matrix(self):
        return glm.translate(glm.mat4(1.0), self.position) * \
                            glm.mat4_cast(self.rotation) * \
                            glm.scale(glm.mat4(1.0), self.scale)

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

        return position, rotation_quat, scale

    def move(self, delta_position: glm.vec3):
        self.position + delta_position
        self.update_position(position=self.position + delta_position)

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