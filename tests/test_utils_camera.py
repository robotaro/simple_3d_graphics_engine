import numpy as np

from src.utilities import utils_camera


def test_screen_to_world_ray():

    view_matrix = np.eye(4, dtype=np.float32)
    view_matrix[:3, 3] = np.array([0, 0, 5])

    projection_matrix = utils_camera.perspective_projection(
        fov_rad=45.0 * np.pi / 180.0,
        z_near=0.1,
        z_far=100.0,
        aspect_ratio=800/600)

    test_conditions = [
        #coord   ray_dir     ray_origin
        ((0, 0), (0, 0, -1), (0, 0, 5)),
        #((0, 0.5), (0, 0.707, -0.707), (0, 0, 5)),  # TODO: WRONG!!!! FIND CORRECT VALUES!!!!!!
    ]

    for conditions in test_conditions:

        viewport_coord = conditions[0]
        target_ray_direction = np.array(conditions[1], dtype=np.float32)
        target_ray_origin = np.array(conditions[2], dtype=np.float32)

        result_ray_direction, result_ray_origin = utils_camera.screen_pos2world_ray(
            camera_matrix=view_matrix,
            projection_matrix=projection_matrix,
            viewport_coord_norm=viewport_coord)

        np.testing.assert_array_equal(target_ray_direction, result_ray_direction)
        np.testing.assert_array_equal(target_ray_origin, result_ray_origin)


def test_world_pos2screen_pos():

    camera_position = np.array([0, 0, 5], dtype=np.float32)
    camera_matrix = np.eye(4, dtype=np.float32)
    camera_matrix[:3, 3] = camera_position
    view_matrix = np.linalg.inv(camera_matrix)

    projection_matrix = utils_camera.perspective_projection(
        fov_rad=45.0 * np.pi / 180.0,
        z_near=0.1,
        z_far=100.0,
        aspect_ratio=1)

    test_world_positions = [
        (0, 0, 0),
        (0, 2.5, 0)
    ]
    target_screen_coordinates = [
        (0, 0),
        (0, -0.47731623)
    ]

    for world_position, target in zip(test_world_positions, target_screen_coordinates):

        result = utils_camera.world_pos2screen_pos(world_position=np.array(world_position, dtype=np.float32),
                                                   projection_matrix=projection_matrix,
                                                   view_matrix=view_matrix,
                                                   camera_position=camera_position)