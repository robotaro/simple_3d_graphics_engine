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


def test_world_pos2viewport_position():

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
        np.array([0, 0], dtype=np.float32),
        #np.array([0, -0.47731623], dtype=np.float32)
        # TODO: THis still not covering it properly! WHy is the Y axis inverted??? FIND OUT!
    ]

    for world_position, target in zip(test_world_positions, target_screen_coordinates):

        result = utils_camera.world_pos2viewport_position(world_position=np.array(world_position, dtype=np.float32),
                                                          projection_matrix=projection_matrix,
                                                          view_matrix=view_matrix)
        np.testing.assert_array_equal(target, result)

