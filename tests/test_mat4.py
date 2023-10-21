import time

import numpy as np

from src.math import mat4


def test_perspective_projection():

    # Example came from ChatGPT, so make look for a more reliable source
    target = np.array([[ 0.5625   ,  0.       ,  0.       ,  0.       ],
                       [ 0.       ,  1.       ,  0.       ,  0.       ],
                       [ 0.       ,  0.       , -1.002002 , -0.2002002],
                       [ 0.       ,  0.       , -1.       ,  0.       ]], dtype=np.float32)

    angle_rad = 45.0 * np.pi / 180.0
    width = 1600
    height = 900

    result = mat4.perspective_projection(
        fovy_rad=angle_rad,
        aspect=width/height,
        far=100.0,
        near=0.1
    )

    np.testing.assert_almost_equal(target, result)


def test_fast_inverse():

    test_matrix = mat4.compute_transform(position=(1, 2, 3),
                                         rotation_rad=(0, .2, .8),
                                         scale=1.0)
    target = np.linalg.inv(test_matrix)
    result = np.eye(4, dtype=np.float32)
    mat4.fast_inverse(in_mat4=test_matrix, out_mat4=result)

    np.testing.assert_almost_equal(target, result)
