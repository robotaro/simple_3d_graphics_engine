from glm import vec3, mat4, dot, length2, sqrt


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


def nearest_point_on_segment(ray_origin: vec3, ray_direction: vec3, segment_start: vec3, segment_end: vec3) -> tuple:
    seg_dir = segment_end - segment_start
    seg_length2 = length2(seg_dir)
    t = dot((ray_origin - segment_start), seg_dir) / seg_length2
    t = max(0, min(1, t))
    nearest_point = segment_start + t * seg_dir
    return nearest_point, t


def distance2_ray_segment(ray_origin: vec3, ray_direction: vec3, p0: vec3, p1: vec3) -> float:
    nearest_point, t = nearest_point_on_segment(ray_origin, ray_direction, p0, p1)
    tr = dot(nearest_point - ray_origin, ray_direction) / dot(ray_direction, ray_direction)
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


def nearest_segment_segment(segment_a_p0: vec3, segment_a_p1: vec3, segment_b_p0: vec3, segment_b_p1: vec3) -> tuple:
    # The tuple returned should contain two floats, representing the point interpolated between
    # p0 and p1 for each segment.
    pass

def nearest_ray_segment(ray_origin: vec3, ray_direction: vec3, segment_b_p0: vec3, segment_b_p1: vec3) -> tuple:
    # The tuple returned should contain two floats, representing the point interpolated between
    # p0 and p1 for each segment.
    pass
