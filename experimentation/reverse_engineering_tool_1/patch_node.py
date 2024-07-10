
class PatchNode:
    def __init__(self, context, origin, sides):
        self.origin = origin
        self.type = [-1, 0, 0, 0]  # [<patch_type>, <rotations>, <x>, <y>]

        self.vert_sides = sides.copy()  # [ side for side in sides]
        self.len_sides = [len(side) - 1 for side in self.vert_sides]
        self.R = None
        self.L = None
        self.divide_line_verts = []
        self.verts_buffer = []
        self.faces_buffer = []
