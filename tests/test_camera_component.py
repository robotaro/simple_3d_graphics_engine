from src.components.camera import Camera


def test_update_viewport():

    params = {"viewport_ratio": (0.25, 0.25, 0.5, 0.5)}

    camera = Camera(parameters=params)
    assert camera.viewport_pixels is None

    camera.update_viewport(window_size=(1600, 900))
    target_viewport_pixels = (400, 225, 800, 450)
    assert target_viewport_pixels == camera.viewport_pixels


def test_is_inside_viewport():

    params = {"viewport_ratio": (0.25, 0.25, 0.5, 0.5)}

    camera = Camera(parameters=params)

    camera.update_viewport(window_size=(800, 600))

    test_conditions = [
        # Coords    Inside or not
        (100, 100,  False),
        (700, 500,  False),
        (-20, 0,    False),
        (400, 300,  True),
        (599, 449,  True),
        (600, 449,  False)]

    for conditions in test_conditions:
        x = conditions[0]
        y = conditions[1]
        target = conditions[2]
        result = camera.is_inside_viewport(coord_pixels=(x, y))
        assert target == result


def test_get_viewport_coordinates():

    params = {"viewport_ratio": (0.25, 0.25, 0.5, 0.5)}

    camera = Camera(parameters=params)

    result = camera.get_viewport_coordinates(screen_coord_pixels=(400, 300))
    assert result is None

    camera.update_viewport(window_size=(800, 600))

    test_conditions = [
        # Coords     Norm Coordinates
        ((400, 300), (0.0, 0.0)),
        ((200, 150), (-1.0, -1.0)),
        ((0, 0), (-2.0, -2.0))  # Invalid scenario, as coordinates should range form -1 to 1
    ]

    for conditions in test_conditions:
        xy_pixel = conditions[0]
        target = conditions[1]
        result = camera.get_viewport_coordinates(screen_coord_pixels=xy_pixel)
        assert target == result
