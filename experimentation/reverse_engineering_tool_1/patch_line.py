
class ControlPoint:
    def __init__(self, co, line):
        self.co = co
        self.handle = mathutils.Vector((0., 0., 1.))
        self.line = line

    def update_location(self, loc):
        dif = self.co - loc
        self.co = loc
        self.handle -= dif


class PatchLine:

    def __init__(self, verts, preexistant, bm, context, ini_cp, ini_line_verts, normal, snap, eagle_eye_ratio,
                 active_objects):

        self.eagle_eye_ratio = eagle_eye_ratio
        if (len(verts) < 2):
            raise Exception("Line must have minimum two verts!")
        self.preexistant = preexistant
        self.bm = bm
        self.context = context
        self.verts = verts

        self.normal = normal
        self.active_objects = active_objects

        self.curves = []
        self.control_points = []
        self.total_control_points = ini_cp
        self.total_created_verts = ini_line_verts

        self._handle_length = 0.5

        self._total_length = 0.

        self.snap = snap

        if (self.preexistant == False):
            self._create_curves()
            self._create_geo()

    def delete_line(self):
        self.delete()
        for v in self.verts:
            if len(v.link_edges) == 0:
                try:
                    bmesh.ops.delete(self.bm, geom=[v], context='VERTS')
                except:
                    print("Could not delete verts!")

    def delete(self):
        if (not self.preexistant):
            if self.total_created_verts > 0:
                delete_verts = [v for v in self.verts[1:-1] if v.is_valid]
                if (len(delete_verts) > 0):
                    self.verts = [self.verts[0], self.verts[-1]]
                    try:
                        bmesh.ops.delete(self.bm, geom=delete_verts, context='VERTS')
                    except:
                        print("Could not delete verts!")
            else:
                if(self.verts[0].is_valid and self.verts[-1].is_valid):
                    new_vert = self.bm.verts.new((self.verts[0].co + self.verts[-1].co) / 2)
                    self.bm.edges.new([self.verts[0], new_vert])
                    self.bm.edges.new([new_vert, self.verts[-1]])
                    self.verts = [self.verts[0], self.verts[-1]]

                    try:
                        del_edge = list(set(self.verts[0].link_edges).intersection(self.verts[-1].link_edges))
                        bmesh.ops.delete(self.bm, geom=del_edge, context='EDGES')
                        bmesh.ops.delete(self.bm, geom=[new_vert], context='VERTS')
                    except:
                        print("Could not delete edge or vert! ", del_edge)

            bmesh.update_edit_mesh(self.context.active_object.data)
            self.context.active_object.data.update_tag()

    def _create_curves(self):

        # init
        self.control_points = []
        self.curves = []

        ini = self.verts[0].co
        end = self.verts[-1].co

        pairs = []

        # form pairs
        for control_point_id in range(self.total_control_points + 1):
            if (control_point_id < self.total_control_points):
                self.control_points.append(
                    ControlPoint(ini.lerp(end, 1.0 / (self.total_control_points + 1) * (control_point_id + 1)), self))
                self.control_points[-1].update_location(
                    get_snap_point(self.context, self.active_objects, self.control_points[-1].co, self.normal,
                                   self.eagle_eye_ratio,
                                   self.snap))

            if (control_point_id == 0 or control_point_id == self.total_control_points):
                if (control_point_id == 0):
                    pairs.append([ini, self.control_points[control_point_id].co])
                if (control_point_id == self.total_control_points):
                    pairs.append([self.control_points[control_point_id - 1].co, end])
            else:
                pairs.append([self.control_points[control_point_id - 1].co, self.control_points[control_point_id].co])

        # create curves
        for i in range(len(pairs)):

            handle1 = pairs[i][0].lerp(pairs[i][1], self._handle_length)
            handle2 = pairs[i][1].lerp(pairs[i][0], self._handle_length)

            if (i < len(pairs) - 1):
                self.control_points[i].handle = handle2

            self.curves.append(
                mathutils.geometry.interpolate_bezier(pairs[i][0], handle1, handle2, pairs[i][1], LINE_RESOLUTION))
            self._total_length += (pairs[i][0] - pairs[i][1]).length

        # end

    def _create_geo(self):
        # create geo

        if (self.total_created_verts < 0):
            self.total_created_verts = 0

        if (self.total_created_verts > MAX_LINE_VERTS):
            self.total_created_verts = MAX_LINE_VERTS

        new_vert = None
        for i in range(self.total_created_verts):

            ratio = 1.0 / (self.total_created_verts + 1) * (i + 1)
            new_vert = self.bm.verts.new(self._get_point_on_line(ratio))
            self.verts.append(self.verts[-1])
            self.verts[i + 1] = new_vert

            if (i == 0):
                self.bm.edges.new([self.verts[0], new_vert])
            if (i == self.total_created_verts - 1):
                self.bm.edges.new([new_vert, self.verts[-1]])
            if (i > 0 and i < self.total_created_verts):
                self.bm.edges.new([self.verts[i], new_vert])

        self._update_verts_location()
        # end

    def _tweak_handle(self, id):
        if (id >= 0 and id < self.total_control_points):
            if (id == 0):
                v1 = (self.verts[0].co - self.control_points[id].co)
                if (id == self.total_control_points - 1):
                    v2 = (self.control_points[id].co - self.verts[-1].co)
                else:
                    v2 = (self.control_points[id].co - self.control_points[id + 1].co)

            elif (id == self.total_control_points - 1):
                v1 = (self.control_points[id - 1].co - self.control_points[id].co)
                v2 = (self.control_points[id].co - self.verts[-1].co)
            else:
                v1 = (self.control_points[id - 1].co - self.control_points[id].co)
                v2 = (self.control_points[id].co - self.control_points[id + 1].co)

            angle = v1.angle(v2, math.pi) * 0.5
            axis = v2.cross(v1)

            R = mathutils.Matrix.Rotation(angle, 4, axis)
            m = (self.control_points[id].handle - self.control_points[id].co).magnitude

            self.control_points[id].handle = v1 @ R * m + self.control_points[id].co

            m1 = v1.magnitude
            m2 = v2.magnitude

            if (m1 < m2):
                length_handle = m1 * self._handle_length
            else:
                length_handle = m2 * self._handle_length

            vh = (self.control_points[id].handle - self.control_points[id].co).normalized() * length_handle
            self.control_points[id].handle = self.control_points[id].co + vh

    def update_line(self, normal, eagle_eye_ratio):
        if (self.preexistant == False):
            self.normal = normal
            self.eagle_eye_ratio = eagle_eye_ratio

            self.curves = []

            ini = self.verts[0].co
            end = self.verts[-1].co

            pairs = []

            # tweak handles
            for i in range(self.total_control_points):
                self._tweak_handle(i - 1)
                self._tweak_handle(i)
                self._tweak_handle(i + 1)

            # form pairs
            for control_point_id in range(self.total_control_points + 1):

                if (control_point_id == 0 or control_point_id == self.total_control_points):
                    if (control_point_id == 0):
                        pairs.append([ini, self.control_points[control_point_id].co])
                    if (control_point_id == self.total_control_points):
                        pairs.append([self.control_points[control_point_id - 1].co, end])
                else:
                    pairs.append(
                        [self.control_points[control_point_id - 1].co, self.control_points[control_point_id].co])

            # create curves
            self._total_length = 0
            for i in range(len(pairs)):
                if (i == 0):
                    handle1 = pairs[i][0].lerp(pairs[i][1], 0.25)
                    handle2 = self.control_points[i].handle

                elif (i < len(pairs) - 1):
                    handle1 = (self.control_points[i - 1].co - self.control_points[i - 1].handle) + self.control_points[
                        i - 1].co
                    handle2 = self.control_points[i].handle

                else:
                    handle1 = (self.control_points[i - 1].co - self.control_points[i - 1].handle) + self.control_points[
                        i - 1].co
                    handle2 = pairs[i][1].lerp(pairs[i][0], 0.25)

                self.curves.append(
                    mathutils.geometry.interpolate_bezier(pairs[i][0], handle1, handle2, pairs[i][1], LINE_RESOLUTION))
                for id in range(len(self.curves[i]) - 1):
                    self._total_length += (self.curves[i][id] - self.curves[i][id + 1]).length

            # update verts location
            self._update_verts_location()
            self.context.area.tag_redraw()

    def _update_verts_location(self):
        for i in range(self.total_created_verts):
            ratio = 1.0 / (self.total_created_verts + 1) * (i + 1)
            self.verts[i + 1].co = self._get_point_on_line(ratio)
        bmesh.update_edit_mesh(self.context.active_object.data)
        self.context.active_object.data.update_tag()

    def _get_point_on_line(self, ratio):
        if (ratio < 0.0):
            return self.verts[0]
        elif (ratio > 1.0):
            return self.verts[-1]

        desired_length = self._total_length * ratio
        length_so_far = 0.0

        current_curve = 0
        current_dot = 0
        last_length = 0.0
        last_vector = None
        while (length_so_far < desired_length and current_curve < len(self.curves)):
            last_vector = self.curves[current_curve][current_dot + 1] - self.curves[current_curve][current_dot]
            last_length = last_vector.length
            length_so_far += last_length
            if (length_so_far > desired_length):
                length_so_far -= last_length
                break

            current_dot += 1
            if (current_dot >= len(self.curves[current_curve]) - 1):
                current_dot = 0
                current_curve += 1

        #if last_length == 0: return self.verts[0]
        rest = desired_length - length_so_far
        if last_length == 0:
            last_length = 1
        rest_ratio = rest / last_length
        rest_vector = (self.curves[current_curve][current_dot + 1] - self.curves[current_curve][
            current_dot]) * rest_ratio

        return self.curves[current_curve][current_dot] + rest_vector

    def change_control_points(self, change):
        new_cp_total = self.total_control_points + change
        if (new_cp_total > 0 and new_cp_total <= MAX_CP):
            # print("Change cp")

            new_cp_locations = []
            for i in range(new_cp_total):
                ratio = 1.0 / (new_cp_total + 1) * (i + 1)
                new_cp_locations.append(self._get_point_on_line(ratio))

            self.total_control_points = new_cp_total

            self._create_curves()

            for i, cp in enumerate(self.control_points):
                cp.update_location(new_cp_locations[i])

            for i in range(len(self.control_points)):
                self.update_line(self.normal, self.eagle_eye_ratio)

    def set_vert_number(self, count):
        if (not self.preexistant):
            self.delete()
            self.total_created_verts = count
            self._create_geo()

    def change_vert_number(self, change):
        if (not self.preexistant and change != 0):
            self.delete()
            self.total_created_verts += change
            self._create_geo()
