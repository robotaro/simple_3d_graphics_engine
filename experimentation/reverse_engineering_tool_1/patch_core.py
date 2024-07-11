import glm
import math

class PatchCore:
    def __init__(self, sides, scale=1.0, alternative=0):
        self.sides = sides
        self.scale = scale
        self.alternative = alternative

        self.vertices = []
        self.faces = []

        self.patch_type = self._get_type([len(side) for side in sides])
        if self.patch_type:
            self._create_mesh()

    def _side_perm(self, len_sides):
        len_sides = len_sides.copy()
        all_one = all(side == 1 for side in len_sides)
        at_least_one = any(side == 1 for side in len_sides)
        if all_one or len(len_sides) < 3 or not at_least_one:
            return [len_sides, 0]

        rotations = 0
        while len_sides[0] == 1 or len_sides[-1] != 1:
            first = len_sides.pop(0)
            len_sides.append(first)
            rotations += 1
        return [len_sides, len(len_sides) - rotations]

    def _get_type(self, len_sides):
        psides, rotationsCW = self._side_perm(len_sides)

        if len(len_sides) == 3:
            if psides == [2, 1, 1]:
                return [0, rotationsCW, 0, 0]
            x = (psides[0] - 4) / 2
            if x >= 0 and int(x) == x and psides[1] == 1 and psides[2] == 1:
                return [10, rotationsCW, int(x), 0]

        elif len(len_sides) == 4:
            if len_sides[0] == len_sides[2] and len_sides[1] == len_sides[3]:
                return [0, 0, len_sides[0] - 1, len_sides[1] - 1]
            if psides == [psides[0], psides[0], 1, 1]:
                return [10, rotationsCW, psides[0] - 2, 0]

        return None

    def _create_mesh(self):
        if not self.patch_type:
            return

        verts = self._generate_vertices()
        self.vertices = verts

        # Generate faces based on patch type
        faces = self._generate_faces(verts)
        self.faces = faces

    def _generate_vertices(self):
        verts = []
        num_sides = len(self.sides)
        angle_step = (2 * math.pi) / num_sides
        for i in range(num_sides):
            angle = i * angle_step
            x = self.scale * math.cos(angle)
            y = self.scale * math.sin(angle)
            verts.append(glm.vec3(x, y, 0))
        return verts

    def _generate_faces(self, verts):
        faces = []
        num_sides = len(self.sides)
        if num_sides == 3:
            faces.append([verts[0], verts[1], verts[2]])
        elif num_sides == 4:
            faces.append([verts[0], verts[1], verts[2], verts[3]])
        # Add more conditions for different patterns based on patch_type
        return faces

    def print_topology(self):
        print("Vertices:")
        for vert in self.vertices:
            print(vert)
        print("Faces:")
        for face in self.faces:
            print(face)

# Example usage:
sides = [[None] * 4, [None] * 4, [None] * 4, [None] * 4]  # Replace with actual vertex references
patch_core = PatchCore(sides, scale=1.0, alternative=0)
patch_core.print_topology()