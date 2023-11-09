from src.components.camera import Camera


def test_update_viewport():

    params = {"viewport_screen_ratio": (0.25, 0.25, 0.5, 0.5)}

    camera = Camera(parameters=params)
    assert camera.viewport_pixels is None

    camera.update_viewport(window_size=(1600, 900))
    target_viewport_pixels = (400, 225, 800, 450)
    assert target_viewport_pixels == camera.viewport_pixels


def test_is_inside_viewport():

    """
    Tests whether a pixel is inside the viewport or not
    :return:
    """

    params = {"viewport_screen_ratio": (0.25, 0.25, 0.5, 0.5)}

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
        result = camera.is_inside_viewport(screen_gl_position=(x, y))
        assert target == result


