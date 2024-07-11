

class Patch:
    def __init__(self, context, bm, frame, sides,
                 first_vert, smooth_iter, smooth_factor,
                 cursor, protected_verts,
                 scale, alternative, smooth_preexistant,
                 snap, eagle_eye_ratio, normal_length, active_objects, tube,
                 border_snap_surface=True):

        self.bm = bm
        self.normal_length = normal_length
        self.first_vert = first_vert

        self.tube = tube
        self.frame = frame

        # create fake vert
        self.fake_vert = None
        if (sum([(len(side) - 1) for side in sides]) % 2 == 1):
            self.fake_vert = self.bm.verts.new((sides[0][0].co + sides[0][1].co) * 0.5)
            self.bm.edges.new([sides[0][0], self.fake_vert])
            self.bm.edges.new([sides[0][1], self.fake_vert])
            sides[0].insert(1, self.fake_vert)

        self.active_objects = active_objects

        self.eagle_eye_ratio = eagle_eye_ratio
        self.smooth_preexistant = smooth_preexistant
        self.border_snap_surface = border_snap_surface

        self.scale = scale
        self.alternative = alternative
        self.protected_verts = protected_verts
        self.context = context
        self.cursor = cursor

        self.smooth_iter = smooth_iter
        self.smooth_factor = smooth_factor
        self.alternative_exists = False
        self.snap = snap

        self.root = PatchNode(context, -1, sides)
        self.set_center()

    def same_same(self, verts):
        if len(self.root.vert_sides) != len(verts):
            return False

        for side in self.root.vert_sides:
            if not side[0] in verts:
                return False
        return True

    def refresh(self, sides):
        self.delete()

        self.fake_vert = None
        if (sum([(len(side) - 1) for side in sides]) % 2 == 1):
            self.fake_vert = self.bm.verts.new((sides[0][0].co + sides[0][1].co) * 0.5)
            self.bm.edges.new([sides[0][0], self.fake_vert])
            self.bm.edges.new([sides[0][1], self.fake_vert])
            sides[0].insert(1, self.fake_vert)

        self.root = PatchNode(context, -1, sides)

        self.process()


    def delete(self):
        self._delete(self.root)

    def _delete(self, node):

        if (node.L != None):
            self._delete(node.R)
            self._delete(node.L)

        if (len(node.divide_line_verts) > 2):
            bmesh.ops.delete(self.bm, geom=node.divide_line_verts[1: len(node.divide_line_verts) - 1], context='VERTS')
            node.divide_line_verts = []

        node.L = None
        node.R = None
        node.type = [-1, 0, 0, 0]

        if (len(node.verts_buffer) > 0):
            del_verts = [v for v in list(set(node.verts_buffer)) if v.is_valid]
            bmesh.ops.delete(self.bm, geom=del_verts, context='VERTS')
            node.verts_buffer = []

        # delete exception
        if (node == self.root):
            del_edges = []

            vert_ring = []
            for side in node.vert_sides:
                for v in side[:-1]:
                    vert_ring.append(v)

            for i, vert in enumerate(vert_ring):
                for edge in vert.link_edges:
                    vn = [v for v in edge.verts if v != vert]
                    for v in vn:
                        if (v in vert_ring and v != vert_ring[(i - 1) % len(vert_ring)] and v != vert_ring[
                            (i + 1) % len(vert_ring)]):
                            del_edges.append(edge)
                            break

            if (len(del_edges) > 0):
                print("Del exception:")
                for de in del_edges:
                    print(de)
                try:
                    bmesh.ops.delete(self.bm, geom=list(set(del_edges)), context='EDGES')
                except Exception as e:
                    print(del_edges)
                    print("Could not delete tricky edge!")
        # end exception

        node.faces_buffer = []

    def print_patch(self):
        next = self.root
        print("\n>  Patch " + len(self.root.vert_sides) + " sides")
        print("   <" + str(self.root.origin) + " " + str(self.root.len_sides) + ", type: " + str(self.root.type) + ">")
        while (next.L != None):
            print("   <" + str(next.L.origin) + " " + str(next.L.len_sides) + ", type: " + str(
                next.L.type) + ">  ---  <" +
                  str(next.R.origin) + " " + str(next.R.len_sides) + ", type: " + str(next.R.type) + ">")
            next = next.L

    def process(self):

        self._reduce(self.root)

        self._create_mesh(self.root)

        if (self.fake_vert != None):
            mrg = [self.root.vert_sides[0][0], self.root.vert_sides[0][1]]
            bmesh.ops.pointmerge(self.bm, verts=mrg, merge_co=self.root.vert_sides[0][0].co)
            del self.root.vert_sides[0][1]
            self.fake_vert = None

        self.smooth()
        self.apply_normal()
        self.snap_surface()

        self.smooth()
        self.apply_normal()
        self.snap_surface()

    def snap_surface(self, normal_length=0.):
        if (self.snap):
            self._snap_surface(self.root, normal_length)

    def _snap_surface(self, node, normal_length=0.):

        if (node.L != None):
            self._snap_surface(node.R)
            self._snap_surface(node.L)

        # clean buffer
        clean = []
        for vert in node.verts_buffer:
            if (vert.is_valid):
                clean.append(vert)
        self.verts_buffer = list(set(clean))

        verts_snap = node.verts_buffer.copy()

        if (self.border_snap_surface):
            for side in self.root.vert_sides:
                for i, vert in enumerate(side):
                    if (vert.is_valid and not vert in self.protected_verts):
                        verts_snap.append(vert)

        if (self.smooth_preexistant):
            for side in self.root.vert_sides:
                for i, vert in enumerate(side):
                    if (vert.is_valid and vert in self.protected_verts and i != 0 and i != len(side) - 1):
                        verts_snap.append(vert)

        for v in verts_snap:
            if (v.is_valid):
                if self.tube:
                    normal = (v.co - mathutils.geometry.intersect_point_line(v.co, self.center, self.center + self.frame.normal)[0]).normalized()
                else:
                    normal = self.frame.normal

                loc = get_snap_point(self.context, self.active_objects, v.co, normal, self.eagle_eye_ratio, True)
                if (loc != None):
                    delta = (v.co - loc).length
                    if delta > self.scale * 0.01:
                        v.co = loc

                else:
                    corners = [side[0].co for side in node.vert_sides]
                    patch_plane_origin = corners[0]
                    for c in corners[1:]:
                        patch_plane_origin += c
                    patch_plane_origin /= len(node.vert_sides)
                    patch_plane_normal = mathutils.geometry.normal(corners)
                    intersection = intersect_line_plane(v.co, v.co + v.normal, patch_plane_origin, patch_plane_normal)
                    if (intersection != None):
                        v.co = intersection

    def apply_normal(self):
        self._apply_normal(self.root)

    def _apply_normal(self, node):
        if (node.L != None):
            self._apply_normal(node.R)
            self._apply_normal(node.L)

        invert = False
        # clean faces_buffer
        clean = []
        for face in node.faces_buffer:
            if (face.is_valid):
                clean.append(face)
        node.faces_buffer = list(set(clean))
        for face in node.faces_buffer:
            if self.frame.normal.dot(face.normal) < 0.1:
                face.normal_flip()

    def smooth(self):
        next = self.root
        verts = next.verts_buffer.copy()
        while (next.L != None):
            for v in next.L.verts_buffer:
                verts.append(v)

            for v in next.R.verts_buffer:
                verts.append(v)

            next = next.L

        verts_for_set = []
        for v in verts:
            if (v.is_valid):
                verts_for_set.append(v)

        border_verts = []
        for side in self.root.vert_sides:
            for i, v in enumerate(side):
                if (self.smooth_preexistant):
                    if not (v in self.protected_verts) or i == len(side) - 1 or i == 0:
                        border_verts.append(v)
                else:
                    border_verts.append(v)

        if (self.smooth_preexistant):
            for side in self.root.vert_sides:
                for i, vert in enumerate(side):
                    if (vert.is_valid and vert in self.protected_verts and i != 0 and i != len(side) - 1):
                        verts_for_set.append(vert)

        verts_list = list(set(verts_for_set).difference(border_verts))

        if (len(verts_list) > 0):
            for i in range(self.smooth_iter):
                bmesh.ops.smooth_vert(self.bm, verts=verts_list, factor=self.smooth_factor, use_axis_x=True,
                                      use_axis_y=True, use_axis_z=True)
                # self.fancy_quad_smooth(verts_list)

    ##############################################################################################################################################
    def fancy_quad_smooth(self, verts_list):

        # print("\nFancy smooth")

        verts = list(set(verts_list))

        bmesh.ops.smooth_vert(self.bm, verts=verts, factor=self.smooth_factor, use_axis_x=True, use_axis_y=True,
                              use_axis_z=True)

        vertsbag = [v for v in verts]

        vert_data = {}  # [[weight, location] ..]

        # [ vertex, vertex_left, vertex_right, vertex_opposite ]
        # get corners list
        corners = []
        for vert in verts:
            for face in vert.link_faces:
                opposite = None
                neighbors = []
                for edge in face.edges:
                    if edge.verts[0] == vert and edge.verts[1] not in verts:
                        neighbors.append(edge.verts[1])
                    elif edge.verts[1] == vert and edge.verts[0] not in verts:
                        neighbors.append(edge.verts[0])

                if len(neighbors) >= 2:
                    corners.append(vert)
                    break

        for corner in corners:
            vertsbag = [v for v in verts]

            current_id = vertsbag.index(corner)

            while len(vertsbag) > 0:

                valid = False
                current_id = (current_id + 1) % len(vertsbag)
                vert = vertsbag[current_id]

                opposite = None
                neighbors = []

                for face in vert.link_faces:
                    if len(face.verts) > 4:
                        continue

                    opposite = None
                    neighbors = []

                    for edge in face.edges:
                        if vert in edge.verts:
                            if vert == edge.verts[0]:
                                if edge.verts[1] not in neighbors:
                                    neighbors.append(edge.verts[1])
                            else:
                                if edge.verts[0] not in neighbors:
                                    neighbors.append(edge.verts[0])

                    for edge in face.edges:
                        if vert not in edge.verts:
                            if edge.verts[0] in neighbors:
                                opposite = edge.verts[1]
                                break
                            else:
                                opposite = edge.verts[0]
                                break

                    if len(neighbors) >= 2 and neighbors[0] not in vertsbag and neighbors[1] not in vertsbag:
                        valid = True
                        break

                if valid:
                    weigth = 0

                    if neighbors[0] not in verts:
                        if neighbors[0] not in vert_data:
                            vert_data[neighbors[0]] = [[0, neighbors[0].co]]
                    if neighbors[1] not in verts:
                        if neighbors[1] not in vert_data:
                            vert_data[neighbors[1]] = [[0, neighbors[1].co]]
                    if opposite != None and opposite not in vert_data:
                        if opposite not in vert_data:
                            vert_data[opposite] = [[0, opposite.co]]

                    if neighbors[0] in vert_data:
                        weigth += vert_data[neighbors[0]][-1][0] + 1

                    if neighbors[1] in vert_data:
                        weigth += vert_data[neighbors[1]][-1][0] + 1

                    if (opposite == None):
                        if vert not in vert_data:
                            vert_data[vert] = [[-1, vert.co]]
                        vertsbag.pop(current_id)
                    else:
                        a = vert_data[neighbors[0]][-1][1]
                        b = vert_data[neighbors[1]][-1][1]
                        c = vert_data[opposite][-1][1]
                        d = mathutils.geometry.intersect_point_line(c, a, b)[0]
                        dy = d - b
                        dx = a - dy
                        loc = dx + (d - c)

                        if vert not in vert_data:
                            vert_data[vert] = []

                        vert_data[vert].append([weigth, loc])

                        vertsbag.pop(current_id)

        vert_list_data = []

        for vert in verts:
            if vert in vert_data:
                # data = [d[0] for d in vert_data[vert]]
                # print(data)

                avg_loc = mathutils.Vector()
                t = 0
                t1 = 0
                for loc in vert_data[vert]:
                    if loc[0] != 0:
                        r = 1 / loc[0]
                        avg_loc += loc[1] * r
                        t += r
                        t1 += loc[0]

                if t != 0:
                    vert.co = vert.co.lerp(avg_loc / t, 1)  # 2 / t1)

    def set_center(self):
        self.center = mathutils.Vector([0, 0, 0])
        count = 0
        if self.tube:
            for v in self.root.vert_sides[0][:-1]:
                count += 1
                self.center += v.co
            for v in self.root.vert_sides[2][:-1]:
                count += 1
                self.center += v.co
            self.center /= count
        else:
            for v in self.root.vert_sides:
                self.center += v[0].co
            self.center /= len(self.root.vert_sides)

    def has_vert(self, vert):
        for side in self.root.vert_sides:
            if vert in side:
                return True
        return False

    def _reduce(self, patch):

        max_d = -1
        max_id = -1
        ln = len(patch.len_sides)
        for i in range(ln):
            d = min(patch.len_sides[(i - 1) % ln], patch.len_sides[(i + 1) % ln]) - 1
            if (d >= max_d):
                max_d = d
                max_id = i

        max_id_p1 = (max_id + 1) % ln
        max_id_m1 = (max_id - 1) % ln

        if (max_d > 0):

            patch.divide_line_verts = self._create_divide_line(
                patch.vert_sides[max_id_m1][(patch.len_sides[max_id_m1] - max_d)],
                patch.vert_sides[max_id_p1][max_d], patch.len_sides[max_id])
            for v in patch.divide_line_verts[1:-1]:
                patch.verts_buffer.append(v)

            patch.R = PatchNode(self.context, max_id,
                                [patch.vert_sides[max_id_m1][(patch.len_sides[max_id_m1] - max_d):],
                                 patch.vert_sides[max_id].copy(),
                                 patch.vert_sides[max_id_p1][0: max_d + 1],
                                 list(reversed(patch.divide_line_verts))])

            patch.R.type = [0, 0, max_d - 1, patch.len_sides[max_id] - 1]

            new_sides = []
            for i in range(len(patch.len_sides)):
                if (i == max_id_m1):
                    new_sides.append(patch.vert_sides[i][0:(patch.len_sides[i] - max_d + 1)])
                elif (i == max_id):
                    new_sides.append(patch.divide_line_verts)
                elif (i == max_id_p1):
                    new_sides.append(patch.vert_sides[i][max_d:])
                else:
                    new_sides.append(patch.vert_sides[i].copy())

            patch.L = PatchNode(self.context, 0, new_sides)
            self._reduce(patch.L)
        else:
            patch.type = self._get_type(patch.len_sides)

    def _side_perm(self, len_sides):
        len_sides = len_sides.copy()
        all_one = True
        for side in len_sides:
            if (side != 1):
                all_one = False
                break

        at_least_one = False
        for side in len_sides:
            if (side == 1):
                at_least_one = True
                break
        if (all_one or len(len_sides) < 3 or (not at_least_one)): return [len_sides, 0]

        rotations = 0
        while (len_sides[0] == 1 or len_sides[-1] != 1):
            first = len_sides[0]
            for i in range(len(len_sides) - 1):
                len_sides[i] = len_sides[i + 1]
            len_sides[-1] = first
            rotations += 1
        return [len_sides, len(len_sides) - rotations]

    def _get_type(self, len_sides):
        psides, rotationsCW = self._side_perm(len_sides)

        # 3 sides
        if (len(len_sides) == 3):
            # P0
            if (psides[0] == 2 and psides[1] == 1 and psides[2] == 1):
                return [0, rotationsCW, 0, 0]

            # P1
            x = (psides[0] - 4) / 2
            if (x >= 0 and int(x) == x and psides[1] == 1 and psides[2] == 1):
                return [10, rotationsCW, int(x), 0]

        # 4 sides
        elif (len(len_sides) == 4):
            # P0
            if (len_sides[0] == len_sides[2] and len_sides[1] == len_sides[3]):
                return [0, 0, len_sides[0] - 1, len_sides[1] - 1]

            # P1
            if (psides[0] == psides[1] and psides[2] == 1 and psides[3] == 1):
                return [10, rotationsCW, psides[0] - 2, 0]

            # P2
            if (psides[0] == (psides[1] - 2) and psides[2] == 1 and psides[3] == 1):
                return [20, rotationsCW, psides[0] - 1, 0]

            # P3
            if (psides[0] == (psides[1] + 2) and psides[2] == 1 and psides[3] == 1):
                return [30, rotationsCW, psides[0] - 3, 0]

            # P4
            x = (psides[0] - 3) / 2
            if (x >= 0 and int(x) == x and psides[1] == 1 and psides[2] == 1 and psides[3] == 1):
                return [40, rotationsCW, int(x), 0]

            # P5
            x = (psides[0] - psides[1] - 2) / 2
            y = psides[1] - 2
            if (x >= 0 and int(x) == x and psides[2] == 1 and psides[3] == 1):
                return [50, rotationsCW, int(x), y]

            # P6
            x = psides[0] - 2
            y = (psides[1] - psides[0] - 2) / 2
            if (y >= 0 and int(y) == y and psides[2] == 1 and psides[3] == 1):
                return [60, rotationsCW, x, int(y)]

        # 5 sides
        elif (len(len_sides) == 5):
            # P0
            if (psides[0] == 2 and psides[1] == 1 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [0, rotationsCW, 0, 0]

            # P1
            x = psides[0] - 2
            if (psides[0] == psides[1] + 1 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [10, rotationsCW, x, 0]

            # P2
            x = psides[0] - 1
            if (psides[0] + 1 == psides[1] and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [20, rotationsCW, x, 0]

            # P3
            x = (psides[0] - 4) / 2
            if (x >= 0 and int(x) == x and psides[1] == 1 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [30, rotationsCW, int(x), 0]

            # P4
            x = (psides[0] - psides[1] - 3) / 2
            y = psides[1] - 2
            if (x >= 0 and int(x) == x and y >= 0 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [40, rotationsCW, int(x), y]

            # P5
            x = psides[0] - 2
            y = (psides[1] - psides[0] - 3) / 2
            if (y >= 0 and int(y) == y and x >= 0 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1):
                return [50, rotationsCW, x, int(y)]

        # 6 sides
        elif (len(len_sides) == 6):
            # P0
            if (psides[0] == psides[3] and psides[1] == 1 and psides[2] == 1 and psides[4] == 1 and psides[5] == 1):
                return [0, rotationsCW, psides[0] - 1, 0]

            # P1
            x = psides[0] - 2
            if (psides[0] == psides[1] and psides[2] == 1 and psides[3] == 1 and psides[4] == 1 and psides[5] == 1):
                return [10, rotationsCW, x, 0]

            # P2
            x = (psides[0] - psides[3] - 2) / 2
            y = psides[3] - 1
            if (x >= 0 and int(x) == x and y >= 0 and psides[1] == 1 and psides[2] == 1 and psides[4] == 1 and psides[
                5] == 1):
                return [20, rotationsCW, int(x), y]

            # P3
            x = (psides[3] - psides[0] - 2) / 2
            y = psides[0] - 1
            if (x >= 0 and int(x) == x and y >= 0 and psides[1] == 1 and psides[2] == 1 and psides[4] == 1 and psides[
                5] == 1):
                return [30, rotationsCW, int(x), y]

            # P4
            x = (psides[0] - psides[1] - 2) / 2
            y = psides[1] - 2
            if (x >= 0 and int(x) == x and y >= 0 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1 and psides[
                5] == 1):
                return [40, rotationsCW, int(x), y]

            # P5
            x = psides[0] - 2
            y = (psides[1] - psides[0] - 2) / 2
            if (x >= 0 and int(x) == x and y >= 0 and psides[2] == 1 and psides[3] == 1 and psides[4] == 1 and psides[
                5] == 1):
                return [50, rotationsCW, int(x), y]

    def _create_divide_line(self, vert_start, vert_end, length):
        new_verts = [vert_start]
        for i in range(length - 1):
            loc = vert_start.co.lerp(vert_end.co, 1.0 / length * (i + 1))

            new_verts.append(self.bm.verts.new(loc))

            self.bm.edges.new([new_verts[-2], new_verts[-1]])
        new_verts.append(vert_end)

        self.bm.edges.new([new_verts[-2], new_verts[-1]])
        return new_verts

    def _create_mesh(self, patch):

        # print ("Create patches:" + str(len(patches.len_sides)) + "." + str(patches.type[0]))

        origin = mathutils.Vector()
        for side in patch.vert_sides:
            origin += side[0].co
        origin /= len(patch.len_sides)

        if (len(patch.len_sides) == 3):
            alternative_solutions = []

            kind = [s // 10 for s in alternative_solutions]
            nos = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            for k in kind:
                nos[k] += 1
            if ((patch.type[0] + (self.alternative % nos[patch.type[0] // 10])) in alternative_solutions):
                patch.type[0] += self.alternative % nos[patch.type[0] // 10]

            if ((patch.type[0] // 10 * 10 + 1) in alternative_solutions):
                self.alternative_exists = True
            else:
                self.alternative_exists = False

            # Pattern 3.0
            if (patch.type[0] == 0):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         ]

                sides = [0, 2, 3]

                faces = [[0, 1, 2, 3],
                         ]

                edgexy = []

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)


            # Pattern 3.1
            elif (patch.type[0] == 10):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [4.0, 0.0, 0.0],  # 4
                         [2.0, 1.0, 0.0],  # 5
                         [2.0, 2.0, 0.0],  # 6
                         ]

                sides = [0, 4, 6]

                faces = [[1, 2, 3, 5],
                         [3, 4, 6, 5],
                         [0, 1, 5, 6],
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

        elif (len(patch.len_sides) == 4):

            alternative_solutions = [21, 22, 31, 32]

            kind = [s // 10 for s in alternative_solutions]
            nos = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            for k in kind:
                nos[k] += 1
            if ((patch.type[0] + (self.alternative % nos[patch.type[0] // 10])) in alternative_solutions):
                patch.type[0] += self.alternative % nos[patch.type[0] // 10]

            if ((patch.type[0] // 10 * 10 + 1) in alternative_solutions):
                self.alternative_exists = True
            else:
                self.alternative_exists = False

            # Pattern 0
            if (patch.type[0] == 0):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [0.0, 1.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         ]

                sides = [0, 1, 2, 3]

                faces = [[0, 1, 2, 3],
                         ]

                edgexy = [0, 1, 1, 2]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 4.1
            elif (patch.type[0] == 10):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [0.0, 2.0, 0.0],  # 5
                         [2.0, 2.0, 0.0],  # 6
                         ]

                sides = [0, 2, 6, 5]

                faces = [[0, 1, 3, 5],
                         [1, 2, 4, 3],
                         [3, 4, 6, 5],
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)


            # Pattern 4.2
            elif (patch.type[0] == 20):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [1.0, 1.0, 0.0],  # 2
                         [1.0, 2.0, 0.0],  # 3
                         [1.0, 3.0, 0.0],  # 4
                         [0.0, 3.0, 0.0],  # 5
                         ]

                sides = [0, 1, 4, 5]

                faces = [[0, 1, 2, 5],  # 0
                         [5, 2, 3, 4],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 21):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [1.0, 1.0, 0.0],  # 2
                         [1.0, 2.0, 0.0],  # 3
                         [1.0, 3.0, 0.0],  # 4
                         [0.0, 3.0, 0.0],  # 5
                         ]

                sides = [0, 1, 4, 5]

                faces = [[0, 1, 2, 3],  # 0
                         [0, 3, 4, 5],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 22):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [3.0, 0.0, 0.0],  # 1
                         [1.0, 1.0, 0.0],  # 2
                         [2.0, 1.0, 0.0],  # 3
                         [2.0, 2.0, 0.0],  # 4
                         [3.0, 2.0, 0.0],  # 5
                         [1.0, 3.0, 0.0],  # 6
                         [3.0, 3.0, 0.0],  # 7
                         [0.0, 4.0, 0.0],  # 8
                         [3.0, 4.0, 0.0],  # 9
                         ]

                sides = [0, 1, 9, 8]

                faces = [[0, 1, 3, 2],  # 0
                         [0, 2, 6, 8],  # 1
                         [2, 3, 4, 6],  # 2
                         [3, 1, 5, 4],  # 3
                         [4, 5, 7, 6],  # 4
                         [6, 7, 9, 8],  # 5
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 4.3
            elif (patch.type[0] == 30):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [3.0, 1.0, 0.0],  # 4
                         [0.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 3, 4, 5]

                faces = [[0, 1, 2, 5],  # 0
                         [2, 3, 4, 5],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 31):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [3.0, 1.0, 0.0],  # 4
                         [0.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 3, 4, 5]

                faces = [[0, 1, 4, 5],  # 0
                         [1, 2, 3, 4],  # 1
                         ]

                edgexy = [1, 2]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 32):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [4.0, 0.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [3.0, 1.0, 0.0],  # 5
                         [1.0, 2.0, 0.0],  # 6
                         [3.0, 2.0, 0.0],  # 7
                         [0.0, 3.0, 0.0],  # 8
                         [4.0, 3.0, 0.0],  # 9
                         ]

                sides = [0, 3, 9, 8]

                faces = [[0, 1, 6, 8],  # 0
                         [1, 2, 4, 6],  # 1
                         [2, 3, 5, 4],  # 2
                         [5, 3, 9, 7],  # 3
                         [4, 5, 7, 6],  # 4
                         [6, 7, 9, 8],  # 5
                         ]

                edgexy = [1, 2]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 4.4
            elif (patch.type[0] == 40):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [1.0, 1.0, 0.0],  # 4
                         [2.0, 1.0, 0.0],  # 5
                         [0.0, 2.0, 0.0],  # 6
                         [3.0, 2.0, 0.0],  # 7
                         ]

                sides = [0, 3, 7, 6]

                faces = [[0, 1, 4, 6],
                         [1, 2, 5, 4],
                         [2, 3, 7, 5],
                         [4, 5, 7, 6],
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)



            # Pattern 4.5
            elif (patch.type[0] == 50):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [4.0, 0.0, 0.0],  # 4
                         [1.0, 1.0, 0.0],  # 5
                         [2.0, 1.0, 0.0],  # 6
                         [3.0, 1.0, 0.0],  # 7
                         [4.0, 1.0, 0.0],  # 8
                         [0.0, 2.0, 0.0],  # 9
                         [4.0, 2.0, 0.0],  # 10
                         ]

                sides = [0, 4, 10, 9]

                faces = [[0, 1, 5, 9],
                         [1, 2, 6, 5],
                         [2, 3, 7, 6],
                         [3, 4, 8, 7],
                         [6, 7, 8, 10],
                         [5, 6, 10, 9],
                         ]

                edgexy = [0, 1, 2, 3]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)


            # Pattern 4.6
            elif (patch.type[0] == 60):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [1.0, 2.0, 0.0],  # 5
                         [2.0, 2.0, 0.0],  # 6
                         [1.0, 3.0, 0.0],  # 7
                         [2.0, 3.0, 0.0],  # 8
                         [0.0, 4.0, 0.0],  # 9
                         [2.0, 4.0, 0.0],  # 10
                         ]

                sides = [0, 2, 10, 9]

                faces = [[0, 1, 3, 5],
                         [1, 2, 4, 3],
                         [3, 4, 6, 5],
                         [5, 6, 8, 7],
                         [7, 8, 10, 9],
                         [0, 5, 7, 9],
                         ]

                edgexy = [0, 1, 2, 4]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

        elif (len(patch.len_sides) == 5):

            alternative_solutions = [11, 21]

            kind = [s // 10 for s in alternative_solutions]
            nos = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            for k in kind:
                nos[k] += 1
            if ((patch.type[0] + (self.alternative % nos[patch.type[0] // 10])) in alternative_solutions):
                patch.type[0] += self.alternative % nos[patch.type[0] // 10]

            if ((patch.type[0] // 10 * 10 + 1) in alternative_solutions):
                self.alternative_exists = True
            else:
                self.alternative_exists = False

            # Pattern 5.0
            if (patch.type[0] == 0):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [2.0, 1.0, 0.0],  # 3
                         [1.0, 2.0, 0.0],  # 4
                         [0.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 2, 3, 4, 5]

                faces = [[0, 1, 4, 5],
                         [1, 2, 3, 4],
                         ]

                edgexy = []

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 5.1
            elif (patch.type[0] == 10):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [2.0, 0.0, 0.0],  # 1
                         [4.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [3.0, 1.0, 0.0],  # 5
                         [0.0, 2.0, 0.0],  # 6
                         [2.0, 2.0, 0.0],  # 7
                         [4.0, 2.0, 0.0],  # 8
                         [2.0, 4.0, 0.0],  # 9
                         ]

                sides = [0, 2, 8, 9, 6]

                faces = [[0, 1, 4, 3],  # 0
                         [1, 2, 5, 4],  # 1
                         [3, 4, 5, 7],  # 2
                         [0, 3, 7, 6],  # 3
                         [5, 2, 8, 7],  # 4
                         [6, 7, 8, 9],  # 5
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 11):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [2.0, 1.0, 0.0],  # 3
                         [1.0, 2.0, 0.0],  # 4
                         [0.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 2, 3, 4, 5]

                faces = [[0, 1, 2, 3],  # 0
                         [0, 3, 4, 5],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 5.2
            elif (patch.type[0] == 20):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [2.0, 0.0, 0.0],  # 1
                         [4.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [3.0, 1.0, 0.0],  # 5
                         [0.0, 2.0, 0.0],  # 6
                         [2.0, 2.0, 0.0],  # 7
                         [4.0, 2.0, 0.0],  # 8
                         [2.0, 4.0, 0.0],  # 9
                         ]

                sides = [6, 0, 2, 8, 9]

                faces = [[0, 1, 4, 3],  # 0
                         [1, 2, 5, 4],  # 1
                         [3, 4, 5, 7],  # 2
                         [0, 3, 7, 6],  # 3
                         [5, 2, 8, 7],  # 4
                         [6, 7, 8, 9],  # 5
                         ]

                edgexy = [0, 6]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            elif (patch.type[0] == 21):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [1.0, 1.0, 0.0],  # 2
                         [1.0, 2.0, 0.0],  # 3
                         [0.0, 2.0, 0.0],  # 4
                         [0.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 1, 3, 4, 5]

                faces = [[0, 1, 2, 3],  # 0
                         [0, 3, 4, 5],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 5.3
            elif (patch.type[0] == 30):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [4.0, 0.0, 0.0],  # 4
                         [1.0, 1.0, 0.0],  # 5
                         [2.0, 1.0, 0.0],  # 6
                         [3.0, 1.0, 0.0],  # 7
                         [0.0, 2.0, 0.0],  # 8
                         [2.0, 3.0, 0.0],  # 9
                         [4.0, 2.0, 0.0],  # 10
                         ]

                sides = [0, 4, 10, 9, 8]

                faces = [[0, 1, 5, 8],  # 0
                         [1, 2, 6, 5],  # 1
                         [2, 3, 7, 6],  # 2
                         [3, 4, 10, 7],  # 3
                         [5, 6, 9, 8],  # 4
                         [6, 7, 10, 9],  # 5
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 5.4
            elif (patch.type[0] == 40):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [4.0, 0.0, 0.0],  # 4
                         [5.0, 0.0, 0.0],  # 5
                         [1.0, 1.0, 0.0],  # 6
                         [2.0, 1.0, 0.0],  # 7
                         [3.0, 1.0, 0.0],  # 8
                         [4.0, 1.0, 0.0],  # 9
                         [5.0, 1.0, 0.0],  # 10
                         [0.0, 2.0, 0.0],  # 11
                         [2.0, 4.0, 0.0],  # 12
                         [5.0, 2.0, 0.0],  # 13
                         ]

                sides = [0, 5, 13, 12, 11]

                faces = [[0, 1, 6, 11],  # 0
                         [1, 2, 7, 6],  # 1
                         [2, 3, 8, 7],  # 2
                         [3, 4, 9, 8],  # 3
                         [4, 5, 10, 9],  # 4
                         [6, 7, 12, 11],  # 5
                         [7, 8, 13, 12],  # 6
                         [8, 9, 10, 13],  # 7
                         ]

                edgexy = [0, 1, 3, 4]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 5.5
            elif (patch.type[0] == 50):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [1.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [1.0, 2.0, 0.0],  # 5
                         [2.0, 2.0, 0.0],  # 6
                         [1.0, 3.0, 0.0],  # 7
                         [2.0, 3.0, 0.0],  # 8
                         [1.0, 4.0, 0.0],  # 9
                         [2.0, 4.0, 0.0],  # 10
                         [0.0, 5.0, 0.0],  # 11
                         [2.0, 5.0, 0.0],  # 12
                         [-2.0, 3.0, 0.0],  # 13
                         ]

                sides = [0, 2, 12, 11, 13]

                faces = [[0, 1, 3, 5],  # 0
                         [1, 2, 4, 3],  # 1
                         [3, 4, 6, 5],  # 2
                         [0, 5, 7, 13],  # 3
                         [5, 6, 8, 7],  # 4
                         [13, 7, 9, 11],  # 5
                         [7, 8, 10, 9],  # 6
                         [9, 10, 12, 11],  # 7
                         ]

                edgexy = [0, 1, 2, 4]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

        elif (len(patch.len_sides) == 6):

            alternative_solutions = [1]

            kind = [s // 10 for s in alternative_solutions]
            nos = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            for k in kind:
                nos[k] += 1
            if ((patch.type[0] + (self.alternative % nos[patch.type[0] // 10])) in alternative_solutions):
                patch.type[0] += self.alternative % nos[patch.type[0] // 10]

            if ((patch.type[0] // 10 * 10 + 1) in alternative_solutions):
                self.alternative_exists = True
            else:
                self.alternative_exists = False

            # Pattern 6.0
            if (patch.type[0] == 1):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 1.0, 0.0],  # 2
                         [1.0, 2.0, 0.0],  # 3
                         [0.0, 2.0, 0.0],  # 4
                         [-1.0, 1.0, 0.0],  # 5
                         [0.0, 1.0, 0.0],  # 6
                         [1.0, 1.0, 0.0],  # 7
                         ]

                sides = [0, 1, 2, 3, 4, 5]

                faces = [[0, 6, 4, 5],  # 0
                         [0, 1, 7, 6],  # 1
                         [1, 2, 3, 7],  # 2
                         [6, 7, 3, 4],  # 3
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            if (patch.type[0] == 0):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 1.0, 0.0],  # 2
                         [1.0, 2.0, 0.0],  # 3
                         [0.0, 2.0, 0.0],  # 4
                         [-1.0, 1.0, 0.0],  # 5
                         ]

                sides = [0, 1, 2, 3, 4, 5]

                faces = [[0, 1, 2, 5],  # 0
                         [5, 2, 3, 4],  # 1
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 6.1
            elif (patch.type[0] == 10):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 1.0, 0.0],  # 3
                         [2.0, 1.0, 0.0],  # 4
                         [1.0, 2.0, 0.0],  # 5
                         [4.0, 2.0, 0.0],  # 6
                         [-2.0, 2.0, 0.0],  # 7
                         [0.0, 4.0, 0.0],  # 8
                         [2.0, 4.0, 0.0],  # 9
                         ]

                sides = [0, 2, 6, 9, 8, 7]

                faces = [[0, 5, 8, 7],  # 0
                         [5, 6, 9, 8],  # 1
                         [4, 3, 6, 5],  # 2
                         [1, 2, 3, 4],  # 3
                         [0, 1, 4, 5],  # 4
                         ]

                edgexy = [0, 1]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 6.2
            elif (patch.type[0] == 20):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [-2.0, 2.0, 0.0],  # 4
                         [1.0, 1.0, 0.0],  # 5
                         [2.0, 1.0, 0.0],  # 6
                         [5.0, 2.0, 0.0],  # 7
                         [1.0, 2.0, 0.0],  # 8
                         [2.0, 2.0, 0.0],  # 9
                         [0.0, 4.0, 0.0],  # 10
                         [3.0, 4.0, 0.0],  # 11
                         ]

                sides = [0, 3, 7, 11, 10, 4]

                faces = [[0, 1, 5, 8],  # 0
                         [1, 2, 6, 5],  # 1
                         [2, 3, 9, 6],  # 2
                         [5, 6, 9, 8],  # 3
                         [0, 8, 10, 4],  # 4
                         [8, 9, 11, 10],  # 5
                         [3, 7, 11, 9],  # 6
                         ]

                edgexy = [0, 1, 1, 2]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 6.3
            elif (patch.type[0] == 30):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [-2.0, 2.0, 0.0],  # 4
                         [1.0, 1.0, 0.0],  # 5
                         [2.0, 1.0, 0.0],  # 6
                         [5.0, 2.0, 0.0],  # 7
                         [1.0, 2.0, 0.0],  # 8
                         [2.0, 2.0, 0.0],  # 9
                         [0.0, 4.0, 0.0],  # 10
                         [3.0, 4.0, 0.0],  # 11
                         ]

                sides = [11, 10, 4, 0, 3, 7]

                faces = [[0, 1, 5, 8],  # 0
                         [1, 2, 6, 5],  # 1
                         [2, 3, 9, 6],  # 2
                         [5, 6, 9, 8],  # 3
                         [0, 8, 10, 4],  # 4
                         [8, 9, 11, 10],  # 5
                         [3, 7, 11, 9],  # 6
                         ]

                edgexy = [0, 1, 1, 2]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 6.4
            elif (patch.type[0] == 40):
                verts = [[0.0, 0.0, 0.0],  # 0
                         [1.0, 0.0, 0.0],  # 1
                         [2.0, 0.0, 0.0],  # 2
                         [3.0, 0.0, 0.0],  # 3
                         [4.0, 0.0, 0.0],  # 4
                         [3.0, 1.0, 0.0],  # 5
                         [5.0, 1.0, 0.0],  # 6
                         [-2.0, 2.0, 0.0],  # 7
                         [1.0, 2.0, 0.0],  # 8
                         [2.0, 2.0, 0.0],  # 9
                         [6.0, 2.0, 0.0],  # 10
                         [1.0, 3.0, 0.0],  # 11
                         [2.0, 3.0, 0.0],  # 12
                         [0.0, 4.0, 0.0],  # 13
                         [4.0, 4.0, 0.0],  # 14
                         ]

                sides = [0, 4, 10, 14, 13, 7]

                faces = [[0, 1, 8, 7],  # 0
                         [1, 2, 9, 8],  # 1
                         [2, 3, 5, 9],  # 2
                         [3, 4, 6, 5],  # 3
                         [5, 6, 10, 9],  # 4
                         [7, 8, 11, 13],  # 5
                         [8, 9, 12, 11],  # 6
                         [9, 10, 14, 12],  # 7
                         [11, 12, 14, 13],  # 8
                         ]

                edgexy = [0, 1, 2, 3]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

            # Pattern 6.5
            elif (patch.type[0] == 50):
                verts = [[-2.0, 2.0, 0.0],  # 0
                         [-1.0, 1.0, 0.0],  # 1
                         [0.0, 0.0, 0.0],  # 2
                         [1.0, 0.0, 0.0],  # 3
                         [2.0, 0.0, 0.0],  # 4
                         [3.0, 0.0, 0.0],  # 5
                         [4.0, 0.0, 0.0],  # 6
                         [1.0, 1.0, 0.0],  # 7
                         [2.0, 2.0, 0.0],  # 8
                         [3.0, 2.0, 0.0],  # 9
                         [6.0, 2.0, 0.0],  # 10
                         [2.0, 3.0, 0.0],  # 11
                         [3.0, 3.0, 0.0],  # 12
                         [0.0, 4.0, 0.0],  # 13
                         [4.0, 4.0, 0.0],  # 14
                         ]

                sides = [0, 2, 6, 10, 14, 13]

                faces = [[2, 3, 7, 1],  # 0
                         [1, 7, 8, 0],  # 1
                         [3, 4, 8, 7],  # 2
                         [4, 5, 9, 8],  # 3
                         [5, 6, 10, 9],  # 4
                         [0, 8, 11, 13],  # 5
                         [8, 9, 12, 11],  # 6
                         [9, 10, 14, 12],  # 7
                         [11, 12, 14, 13],  # 8
                         ]

                edgexy = [0, 1, 2, 3]

                self._pattern(origin, verts, sides, faces, edgexy, type, patch)

        if (patch.R != None):
            self._create_mesh(patch.R)
        if (patch.L != None):
            self._create_mesh(patch.L)

    def _pattern(self, origin, verts, sides, faces, edgexy, type, patch):
        v = []
        up = mathutils.Vector((0., 0., 1.))
        right = mathutils.Vector((1., 0., 0.))
        angle = self.frame.normal.angle(up)
        axis = self.frame.normal.cross(up)
        for vec in verts:
            loc = mathutils.Vector(vec) * self.scale + origin
            loc = rotate_point(loc, angle, axis, origin)
            v.append(self.bm.verts.new(loc))

        for vt in v:
            patch.verts_buffer.append(vt)

        if (len(edgexy) >= 2):
            edge_x = self.bm.edges.new([v[edgexy[0]], v[edgexy[1]]])
        if (len(edgexy) == 4):
            edge_y = self.bm.edges.new([v[edgexy[2]], v[edgexy[3]]])

        face = []
        for f in faces:
            face.append(self.bm.faces.new([v[f[0]], v[f[1]], v[f[2]], v[f[3]]]))
            patch.faces_buffer.append(face[-1])

        # divide
        new_faces = []
        if (patch.type[2] > 0):
            xring = get_edge_rings(edge_x)
            for face in bmesh.ops.subdivide_edgering(self.bm, edges=xring, cuts=patch.type[2])['faces']:
                new_faces.append(face)
                patch.faces_buffer.append(face)

        if (patch.type[3] > 0):
            yring = get_edge_rings(edge_y)
            for face in bmesh.ops.subdivide_edgering(self.bm, edges=yring, cuts=patch.type[3])['faces']:
                new_faces.append(face)
                patch.faces_buffer.append(face)

        for face in new_faces:
            for vert in face.verts:
                patch.verts_buffer.append(vert)

        # set lines
        lines = []
        for i in range(len(sides)):
            lines.append(crawl_straight_line(self.bm, v[sides[i]], v[sides[(i + 1) % len(sides)]]))

        # rotate
        for r in range(patch.type[1]):
            line_swap = lines[0]
            for i in range(len(lines) - 1):
                lines[i] = lines[i + 1]
            lines[-1] = line_swap

        # link verts
        for i in range(len(lines)):
            # print("len side: "+ str(len(patches.vert_sides[i])) + " len lines: "+ str(len(lines[i])))
            for j in range(len(lines[i]) - 1):
                if patch.vert_sides[i][j].is_valid and lines[i][j].is_valid:
                    mrg = [patch.vert_sides[i][j], lines[i][j]]
                    bmesh.ops.pointmerge(self.bm, verts=mrg, merge_co=patch.vert_sides[i][j].co)

