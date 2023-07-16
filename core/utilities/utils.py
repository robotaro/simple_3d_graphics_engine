
import os
import subprocess

import numpy as np

from scipy.interpolate import CubicSpline

# TODO

def interpolate_positions(positions: np.array, ts_in, ts_out):
    """
    Interpolate positions given at timestamps `ts_in` to timestamps given at `ts_out` with a cubic spline.
    :param positions: A numpy array of shape (F, N, 3), i.e. in angle-axis form.
    :param ts_in: Timestamps corresponding to the given positions, len(ts_in) == F
    :param ts_out: The desired output timestamps.
    :return: A numpy array of shape (len(ts_out), N, 3).
    """
    cs = CubicSpline(ts_in, positions, axis=0)
    new_positions = cs(ts_out)
    return new_positions


def resample_positions(positions, fps_in, fps_out):
    """
    Resample 3D positions from `fps_in` to `fps_out`.
    :param positions: A numpy array of shape (F, ...).
    :param fps_in: The frequency of the input sequence.
    :param fps_out: The desired output frequency.
    :return: A numpy array of shape (F', ...) where F is adjusted according to the new fps.
    """
    n_frames = positions.shape[0]
    assert n_frames > 1, "Resampling with one data point does not make sense."
    duration = n_frames / fps_in
    ts_in = np.arange(0, duration, 1 / fps_in)[:n_frames]
    ts_out = np.arange(0, duration, 1 / fps_out)
    return interpolate_positions(positions, ts_in, ts_out)


def compute_vertex_and_face_normals_torch(vertices, faces, vertex_faces, normalize=False):
    """
    Compute (unnormalized) vertex normals for the given vertices.
    :param vertices: A tensor of shape (N, V, 3).
    :param faces: A tensor of shape (F, 3) indexing into `vertices`.
    :param vertex_faces: A tensor of shape (V, MAX_VERTEX_DEGREE) that lists the face IDs each vertex is a part of.
    :param normalize: Whether to make the normals unit length or not.
    :return: The vertex and face normals as tensors of shape (N, V, 3) and (N, F, 3) respectively.
    """
    vs = vertices[:, faces.to(dtype=torch.long)]
    face_normals = torch.cross(vs[:, :, 1] - vs[:, :, 0], vs[:, :, 2] - vs[:, :, 0], dim=-1)  # (N, F, 3)

    ns_all_faces = face_normals[:, vertex_faces]  # (N, V, MAX_VERTEX_DEGREE, 3)
    ns_all_faces[:, vertex_faces == -1] = 0.0
    vertex_degrees = (vertex_faces > -1).sum(dim=-1).to(dtype=ns_all_faces.dtype)
    vertex_normals = ns_all_faces.sum(dim=-2) / vertex_degrees[None, :, None]  # (N, V, 3)

    if normalize:
        face_normals = face_normals / torch.norm(face_normals, dim=-1).unsqueeze(-1)
        vertex_normals = vertex_normals / torch.norm(vertex_normals, dim=-1).unsqueeze(-1)

    return vertex_normals, face_normals


def compute_vertex_and_face_normals(vertices, faces, vertex_faces, normalize=False):
    """
    Compute (unnormalized) vertex normals for the given vertices. This is a rather expensive operation despite it being
    fully optimized with numpy. For a typical SMPL mesh this can take 5-10ms per call. Not normalizing the resulting
    normals speeds things up considerably, so we are omitting this as OpenGL shaders can do this much more efficiently.
    For more speedup, consider caching the result of this function.

    :param vertices: A numpy array of shape (N, V, 3).
    :param faces: A numpy array of shape (F, 3) indexing into `vertices`.
    :param vertex_faces: A numpy array of shape (V, MAX_VERTEX_DEGREE) that lists the face IDs each vertex is a part of.
    :param normalize: Whether to normalize the normals or not.
    :return: The vertex and face normals as a np arrays of shape (N, V, 3) and (N, F, 3) respectively.
    """
    vs = vertices[:, faces]
    face_normals = np.cross(vs[:, :, 1] - vs[:, :, 0], vs[:, :, 2] - vs[:, :, 0], axis=-1)  # (N, F, 3)

    ns_all_faces = face_normals[:, vertex_faces]  # (N, V, MAX_VERTEX_DEGREE, 3)
    ns_all_faces[:, vertex_faces == -1] = 0.0
    vertex_degrees = np.sum(vertex_faces > -1, axis=-1)
    vertex_normals = np.sum(ns_all_faces, axis=-2) / vertex_degrees[np.newaxis, :, np.newaxis]  # (N, V, 3)

    if normalize:
        face_normals = face_normals / np.linalg.norm(face_normals, axis=-1)[..., np.newaxis]
        vertex_normals = vertex_normals / np.linalg.norm(vertex_normals, axis=-1)[..., np.newaxis]

    return vertex_normals, face_normals


def compute_vertex_and_face_normals_sparse(vertices, faces, vertex_faces_sparse, normalize=False):
    """
    Compute (unnormalized) vertex normals for the given vertices. This is a rather expensive operation despite it being
    fully optimized with numpy. For a typical SMPL mesh this can take 5-10ms per call. Not normalizing the resulting
    normals speeds things up considerably, so we are omitting this as OpenGL shaders can do this much more efficiently.
    For more speedup, consider caching the result of this function.

    :param vertices: A numpy array of shape (N, V, 3).
    :param faces: A numpy array of shape (F, 3) indexing into `vertices`.
    :param vertex_faces: A scipy sparse adjacency matrix shape (V, F), each row contains a one for all faces
        that are adjacent to the corresponding vertex and a 0 otherwise.
    :param normalize: Whether to normalize the normals or not.
    :return: The vertex and face normals as a np arrays of shape (N, V, 3) and (N, F, 3) respectively.
    """
    triangles = vertices[:, faces]
    vectors = np.diff(triangles, axis=2)
    crosses = np.cross(vectors[:, :, 0], vectors[:, :, 1])

    normals = np.moveaxis(crosses, 0, 2)
    normals = normals.reshape((normals.shape[0], -1))
    vn = vertex_faces_sparse.dot(normals)
    vn = vn.reshape((vn.shape[0], 3, -1))
    vn = np.moveaxis(vn, 2, 0)

    if normalize:
        crosses = crosses / np.linalg.norm(crosses, axis=-1)[..., np.newaxis]
        vn = vn / np.linalg.norm(vn, axis=-1)[..., np.newaxis]

    return vn, crosses


def spherical_coordinates_from_direction(v, degrees=False):
    """
    Converts from a normalized direction vector to spherical coordinates.

    :param v: direction vector as np array of shape (3)
    :param degrees: if True returned spherical coordinates are expressed in degrees.
    :return: elevation and azimuthal angles
    """
    theta = np.arcsin(v[1])
    phi = np.arctan2(v[2], v[0])
    phi = np.remainder(phi, np.pi * 2.0)
    if degrees:
        return np.degrees(theta), np.degrees(phi)
    else:
        return theta, phi


def direction_from_spherical_coordinates(theta, phi, degrees=False):
    """
    Converts from spherical coordinates to a direction vector.

    :param theta: elevation angle from -PI/2 to PI/2, 0 represents the horizon and PI/2 and -PI/2 the +y and -y directions respectively
    :param phi: azimuthal angle from 0 to 2 * PI, 0 and PI represents the +x and -x directions respectively
        PI/2 and 3/2P the +z and -z respectively.
    :param degrees: if True theta and phi must be expressed in degrees instead.
    :return: The normalized direction as a np array of shape (3)
    """
    if degrees:
        theta, phi = np.radians(theta), np.radians(phi)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)

    x = cos_theta * cos_phi
    y = sin_theta
    z = cos_theta * sin_phi

    return np.array([x, y, z])


def set_lights_in_program(prog, lights, shadows_enabled, ambient_strength):
    """Set program lighting from scene lights"""
    for i, light in enumerate(lights):
        prog[f"dirLights[{i}].direction"].value = tuple(light.direction)
        prog[f"dirLights[{i}].color"].value = light.light_color
        prog[f"dirLights[{i}].strength"].value = light.strength if light.enabled else 0.0
        prog[f"dirLights[{i}].shadow_enabled"].value = shadows_enabled and light.shadow_enabled
    prog["ambient_strength"] = ambient_strength


def set_material_properties(prog, material):
    prog["diffuse_coeff"].value = material.diffuse
    prog["ambient_coeff"].value = material.ambient


def compute_union_of_bounds(nodes):
    if len(nodes) == 0:
        return np.zeros((3, 2))

    bounds = np.array([[np.inf, np.NINF], [np.inf, np.NINF], [np.inf, np.NINF]])
    for n in nodes:
        child = n.bounds
        bounds[:, 0] = np.minimum(bounds[:, 0], child[:, 0])
        bounds[:, 1] = np.maximum(bounds[:, 1], child[:, 1])
    return bounds


def compute_union_of_current_bounds(nodes):
    if len(nodes) == 0:
        return np.zeros((3, 2))

    bounds = np.array([[np.inf, np.NINF], [np.inf, np.NINF], [np.inf, np.NINF]])
    for n in nodes:
        child = n.current_bounds
        bounds[:, 0] = np.minimum(bounds[:, 0], child[:, 0])
        bounds[:, 1] = np.maximum(bounds[:, 1], child[:, 1])
    return bounds
