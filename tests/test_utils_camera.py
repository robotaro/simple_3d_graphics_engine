import numpy as np

from src.utilities import utils_camera

def test_screen_position_pixels2viewport_position():

    params = {"viewport_ratio": (0.25, 0.25, 0.5, 0.5)}

    screen_size = (400, 300)
    viewport_pixels = (200, 150, 400, 300)

    test_conditions = [
        # screen     viewport
        ((400, 300), (0.0, 0.0)),
        ((500, 375), (0.5, -0.5)),
        ((600, 450), (1.0, -1.0)),
        ((200, 150), None),
        ((0, 0), None)  # Invalid scenario, as coordinates should range form -1 to 1
    ]

    for conditions in test_conditions:
        xy_pixel = conditions[0]
        target = conditions[1]
        result = utils_camera.screen_position_pixels2viewport_position(screen_position_pixels=xy_pixel,
                                                                       viewport_pixels=viewport_pixels)
        assert target == result


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
        (0, 0),
        (0, -0.47731623)
    ]

    for world_position, target in zip(test_world_positions, target_screen_coordinates):

        result = utils_camera.world_pos2viewport_position(world_position=np.array(world_position, dtype=np.float32),
                                                          projection_matrix=projection_matrix,
                                                          view_matrix=view_matrix)
        assert target == result

