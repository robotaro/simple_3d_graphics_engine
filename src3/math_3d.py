from glm import vec3, mat4, dot, length2, sqrt, epsilon, cross, normalize


def intersect_ray_plane_boolean(ray_origin: vec3, ray_direction: vec3, plane_normal: vec3, plane_offset: float) -> bool:
    denom = dot(plane_normal, ray_direction)
    if denom == 0.0:
        return False  # The ray is parallel to the plane

    t = (dot(plane_normal, plane_normal * plane_offset) - dot(plane_normal, ray_origin)) / denom
    return t >= 0.0


def intersect_ray_plane(ray_origin: vec3, ray_direction: vec3, plane_normal: vec3, plane_offset: float) -> tuple:
    denom = dot(plane_normal, ray_direction)
    if denom == 0.0:
        return False, None

    t = (dot(plane_normal, plane_normal * plane_offset) - dot(plane_normal, ray_origin)) / denom
    if t < 0.0:
        return False, None

    return True, t


def ray_intersect_plane_coordinates(plane_origin, plane_vec1, plane_vec2, ray_origin, ray_direction) -> tuple:

    # Normalize the plane vectors to ensure they have unit length
    plane_vec1 = normalize(plane_vec1)
    plane_vec2 = normalize(plane_vec2)

    # Calculate the normal of the plane
    plane_normal = cross(plane_vec1, plane_vec2)

    # Offset is the distance from the origin to the plane along the plane normal
    plane_offset = dot(plane_normal, plane_origin)

    # Find the intersection of the ray with the plane
    intersect, t = intersect_ray_plane(ray_origin, ray_direction, plane_normal, plane_offset)
    if not intersect:
        return None, None, None  # No intersection

    # Calculate the intersection point
    intersection_point = ray_origin + t * ray_direction

    # Project the intersection point onto the plane vectors
    relative_intersection = intersection_point - plane_origin
    u_coord = dot(relative_intersection, plane_vec1)
    v_coord = dot(relative_intersection, plane_vec2)

    return u_coord, v_coord, t


def intersect_ray_sphere_boolean(ray_origin: vec3,
                                 ray_direction: vec3,
                                 sphere_origin: vec3,
                                 sphere_radius: float) -> bool:
    p = sphere_origin - ray_origin
    p2 = length2(p)
    q = dot(p, ray_direction)
    r2 = sphere_radius * sphere_radius
    if q < 0.0 and p2 > r2:
        return False

    return p2 - (q * q) <= r2


def intersect_ray_sphere(ray_origin: vec3, ray_direction: vec3, sphere_origin: vec3, sphere_radius: float) -> tuple:
    p = sphere_origin - ray_origin
    q = dot(p, ray_direction)
    if q < 0.0:
        return False, None, None

    p2 = length2(p) - q * q
    r2 = sphere_radius * sphere_radius
    if p2 > r2:
        return False, None, None

    s = sqrt(r2 - p2)
    t0_ = max(q - s, 0.0)
    t1_ = q + s

    return True, t0_, t1_


def nearest_point_on_segment(ray_origin: vec3, ray_direction: vec3, p0: vec3, p1: vec3) -> tuple:

    """
    The variable tr represents the parameter value along the ray direction that gives
    the nearest point on the ray to the closest point on the segment
    """

    ldir = p1 - p0
    p = p0 - ray_origin
    q = length2(ldir)
    r = dot(ldir, ray_direction)
    s = dot(ldir, p)
    t = dot(ray_direction, p)

    denom = q - r * r
    if denom < epsilon():
        sd = td = 1.0
        sn = 0.0
        tn = t
    else:
        sd = td = denom
        sn = r * t - s
        tn = q * t - r * s
        if sn < 0.0:
            sn = 0.0
            tn = t
            td = 1.0
        elif sn > sd:
            sn = sd
            tn = t + r
            td = 1.0

    if tn < 0.0:
        tr = 0.0
        if r >= 0.0:
            ts = 0.0
        elif s <= q:
            ts = 1.0
        else:
            ts = -s / q
    else:
        tr = tn / td
        ts = sn / sd

    nearest_point = p0 + ldir * ts
    return nearest_point, tr


def distance2_ray_segment(ray_origin: vec3, ray_direction: vec3, p0: vec3, p1: vec3) -> float:
    """
    Returns squared shortest perpendicular distance between segment and ray
    """
    nearest_point, tr = nearest_point_on_segment(ray_origin, ray_direction, p0, p1)
    p = ray_origin + ray_direction * tr
    return length2(p - nearest_point)


def intersect_ray_capsule_boolean(ray_origin: vec3, ray_direction: vec3, p0: vec3, p1: vec3, radius: float) -> bool:
    return distance2_ray_segment(ray_origin, ray_direction, p0, p1) < radius * radius


def intersect_ray_capsule(ray_origin: vec3, ray_direction: vec3, p0: vec3, p1: vec3, radius: float) -> tuple:
    if intersect_ray_capsule_boolean(ray_origin, ray_direction, p0, p1, radius):
        # Placeholder values for t0_ and t1_
        t0_ = 0.0
        t1_ = 0.0
        return True, t0_, t1_
    else:
        return False, None, None
