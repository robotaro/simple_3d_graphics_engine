import numpy as np

from src.utilities import utils_camera


def test_screen_gl_position_pixels2viewport_position():

    """
    This test condition has one viewport on the left covering half of the screen, and two on the right,
    covering each top and bottom quarters.
    :return:
    """

    test_conditions = [
        # gl_pixels    viewport_pixels  target_viewport_position
        ((400, 450), (0, 0, 800, 900), (0, 0)),
        ((1200, 675), (800, 450, 800, 450), (0, 0)),
        ((1200, 1025), (800, 0, 800, 450), None)
    ]

    for gl_pixels, viewport_pixels, target_viewport_position in test_conditions:

        result = utils_camera.screen_gl_position_pixels2viewport_position(position_pixels=gl_pixels,
                                                                          viewport_pixels=viewport_pixels)
        assert target_viewport_position == result


def test_screen_to_world_ray():

    camera_matrix = np.eye(4, dtype=np.float32)
    camera_matrix[:3, 3] = np.array([0, 0, 5])

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
            viewport_coord,
            camera_matrix,
            projection_matrix)

        np.testing.assert_array_equal(target_ray_direction, result_ray_direction)
        np.testing.assert_array_equal(target_ray_origin, result_ray_origin)

