import numpy as np
from numba import njit, float32

from src.core import constants
from src.math import mat4


@njit(cache=True)
def get_gizmo_scale(camera_matrix: np.ndarray, object_position: np.array) -> float:

    view_matrix = np.eye(4, dtype=np.float32)
    mat4.fast_inverse(in_mat4=camera_matrix, out_mat4=view_matrix)
    position_camera = mat4.mul_vector3(in_mat4=view_matrix, in_vec3=object_position)
    scale = -position_camera[2] * constants.GIZMO_3D_SCALE_COEFFICIENT
    return scale


#@njit(float32[:](float32[:, :], float32[:, :], float32[:]), cache=True)
def world_pos2viewport_position(view_matrix: np.ndarray,
                                projection_matrix: np.ndarray,
                                world_position: np.array) -> np.array:

    """view_projection_position = mat4.mul_vector3(in_mat4=projection_matrix @ view_matrix, in_vec3=world_position)

    # Z-Zc=F
    # X' = X * (F/Z)
    # Y' = Y * (F/Z)

    coefficient = (view_projection_position[2] - camera_position[2]) / view_projection_position[2]
    screen_x = view_projection_position[0] * coefficient
    screen_y = view_projection_position[1] * coefficient

    return screen_x, screen_y
    """
    # Create a 4D vector for the object's world position
    object_position_4d = np.append(world_position, 1)

    # Transform the object's world position to camera space
    object_camera_position = np.dot(np.linalg.inv(view_matrix), object_position_4d)

    # Project the object's camera space position onto the image plane
    projected_position = np.dot(projection_matrix, object_camera_position)

    # Perform perspective divide
    projected_position /= projected_position[3]

    # The x and y coordinates on the screen are now the first two elements of projected_position
    screen_coordinates = projected_position[:2]

    return screen_coordinates


#@njit(cache=True)
def world_pos2screen_pixels(view_matrix: np.ndarray,
                            viewport_pixels: tuple,
                            projection_matrix: np.ndarray,
                            world_position: np.array):

    viewport_position = world_pos2viewport_position(view_matrix=view_matrix,
                                                    projection_matrix=projection_matrix,
                                                    world_position=world_position)

    # TODO: Y-axis is reversed to get positive Y-axis pointing up. Check if this is because of the projection matrix
    screen_x = viewport_pixels[2] * (viewport_position[0] + 1.0) / 2.0 + viewport_pixels[0]
    screen_y = viewport_pixels[3] * (-viewport_position[1] + 1.0) / 2.0 + viewport_pixels[1]

    return screen_x, screen_y


def screen_position_pixels2viewport_position(screen_position_pixels: tuple, viewport_pixels: tuple) -> tuple:

    """
    Screen's origin is the left-upper corner with positive x to the RIGHT and positive y DOWN
    Viewports origin is at the center with positive x to the RIGHT and positive y UP

    :param screen_position_pixels: (x, y) <float32>
    :param viewport_pixels: tuple (x, y, width, height) <float32>
    :return: Relative
    """

    if screen_position_pixels[0] < viewport_pixels[0]:
        return None

    if screen_position_pixels[0] > viewport_pixels[0] + viewport_pixels[2]:
        return None

    if screen_position_pixels[1] < viewport_pixels[0]:
        return None

    if screen_position_pixels[1] > viewport_pixels[1] + viewport_pixels[3]:
        return None

    x_normalised = (screen_position_pixels[0] - viewport_pixels[0]) / viewport_pixels[2]
    y_normalised = (screen_position_pixels[1] - viewport_pixels[1]) / viewport_pixels[3]

    x_viewport = (x_normalised - 0.5) * 2.0
    y_viewport = (y_normalised - 0.5) * 2.0

    return x_viewport, y_viewport


@njit(cache=True)
def screen_pos2world_ray(viewport_coord_norm: tuple,
                         camera_matrix: np.ndarray,
                         projection_matrix: np.ndarray):

    """
    Viewport coordinates are +1 to the right, -1 to the left, +1 up and -1 down. Zero at the centre for both axes

    :param viewport_coord_norm: tuple, (x, y) <float, float> Ranges between -1 and 1
    :param camera_matrix: np.ndarray (4, 4) <float32> Do NOT confuse this with the "view_matrix"!
                          This is the transform of the camera in space, simply as you want the camera to be placed
                          in the scene. the view_matrix is the INVERSE of the camera_matrix :)

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
    world_coordinates = np.dot(camera_matrix, eye_coordinates)

    # Extract the ray's origin from the inverted view matrix
    ray_origin = np.ascontiguousarray(camera_matrix[:, 3][:3])  # When extracting vectors, they need to be continuous!

    # Normalize the world coordinates to get the ray direction
    ray_direction = np.ascontiguousarray(world_coordinates[:3])
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