import numpy as np
from numba import njit


@njit
def screen_to_world_ray(viewport_coord_norm: tuple,
                        view_matrix: np.ndarray,
                        projection_matrix: np.ndarray):

    """

    :param viewport_coord_norm: tuple, (x, y) <float, float> Ranges between -1 and 1
    :param view_matrix: np.ndarray (4, 4) <float32> position and orientation of camera in space
    :param projection_matrix: (4, 4) <float32> perspective matrix

    :return:
    """

    # Create a 4D homogeneous clip space coordinate
    clip_coordinates = np.array([viewport_coord_norm[0], viewport_coord_norm[1], -1.0, 1.0], dtype=np.float32)

    # Inverse the projection matrix to get the view coordinates
    inv_projection_matrix = np.linalg.inv(projection_matrix)
    eye_coordinates = np.dot(inv_projection_matrix, clip_coordinates)
    eye_coordinates = np.array([eye_coordinates[0], eye_coordinates[1], -1.0, 0.0], dtype=np.float32)

    # Inverse the view matrix to get the world coordinates
    world_coordinates = np.dot(view_matrix, eye_coordinates)

    # Extract the ray's origin from the inverted view matrix
    ray_origin = view_matrix[:, 3][:3]

    # Normalize the world coordinates to get the ray direction
    ray_direction = world_coordinates[:3]
    ray_direction[1] = -ray_direction[1]  # TODO: FIND OUT WHY THE Y-AXIS IS REVERSED!!!!!! VERY IMPORTANT!!!a
    ray_direction /= np.linalg.norm(ray_direction)

    return ray_direction, ray_origin


def orthographic_projection(scale_x: float, scale_y: float, z_near: float, z_far: float):
    """Returns an orthographic projection matrix."""
    projection = np.zeros((4, 4), dtype=np.float32)
    projection[0, 0] = 1.0 / scale_x
    projection[1, 1] = 1.0 / scale_y
    projection[2, 2] = 2.0 / (z_near - z_far)
    projection[2, 3] = (z_far + z_near) / (z_near - z_far)
    projection[3, 3] = 1.0
    return projection


def perspective_projection(fov_rad: float, aspect_ratio: float, z_near: float, z_far: float):
    """Returns a perspective projection matrix."""
    ar = aspect_ratio
    t = np.tan(fov_rad / 2.0)

    projection = np.zeros((4, 4), dtype=np.float32)
    projection[0, 0] = 1.0 / (ar * t)
    projection[1, 1] = 1.0 / t
    projection[3, 2] = -1.0

    f, n = z_far, z_near
    if f is None:
        projection[2, 2] = -1.0
        projection[2, 3] = -2.0 * n
    else:
        projection[2, 2] = (f + n) / (n - f)
        projection[2, 3] = (2 * f * n) / (n - f)

    return projection

"""

@njit
def screen_to_world_ray(screen_coords_normalised: tuple,
                        view_matrix: np.ndarray,
                        projection_matrix: np.ndarray,
                        output_ray_origin: np.array,
                        output_ray_direction: np.array):
                        
    # :param output_ray_origin: np.array (3,) <float32> origin of ray matching the camera's view matrix
    #     :param output_ray_direction: np.array (3,) <float32> direction of ray

    # Create a 4D homogeneous clip space coordinate
    clip_coordinates = np.array([screen_coords_normalised[0], screen_coords_normalised[1], -1.0, 1.0])

    # Inverse the projection matrix to get the view coordinates
    inv_projection_matrix = np.linalg.inv(projection_matrix)
    eye_coordinates = np.dot(inv_projection_matrix, clip_coordinates)
    eye_coordinates = np.array([eye_coordinates[0], eye_coordinates[1], -1.0, 0.0])

    # Inverse the view matrix to get the world coordinates
    inv_view_matrix = np.linalg.inv(view_matrix)
    world_coordinates = np.dot(inv_view_matrix, eye_coordinates)

    # Extract the ray's origin from the inverted view matrix
    output_ray_origin = inv_view_matrix[:, 3][:3]

    # Normalize the world coordinates to get the ray direction
    output_ray_direction = world_coordinates[:3]
    output_ray_direction /= np.linalg.norm(output_ray_direction)

"""