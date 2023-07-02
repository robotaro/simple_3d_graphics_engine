import glm


class Node:

    def __init__(self, name='', mesh_index=None):
        self.name = name
        self.mesh_index = mesh_index
        self.local_matrix = glm.mat4(1)
        self.world_matrix = glm.mat4(1)
        self.rotation = glm.vec3(0)
        self.translation = glm.vec3(0)
        self.scale = glm.vec3(1)
        self.child_indices = []

    def add_child_node_index(self, index: int):
        self.child_indices.append(index)

    def add_children_node_indices(self, indices: list):
        self.child_indices += indices

