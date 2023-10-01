import numpy as np

from ecs.utilities import utils_camera


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

        result_ray_direction, result_ray_origin = utils_camera.screen_to_world_ray(
            view_matrix=view_matrix,
            projection_matrix=projection_matrix,
            viewport_coord_norm=viewport_coord)

        np.testing.assert_array_equal(target_ray_direction, result_ray_direction)
        np.testing.assert_array_equal(target_ray_origin, result_ray_origin)
