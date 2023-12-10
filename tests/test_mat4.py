import time

import numpy as np

from src.math import mat4


def test_matrix_composition_eye():
    target_translation = np.array([0, 0, 0], dtype=np.float32)
    target_rotation = np.array([0, 0, 0, 1], dtype=np.float32)  # quaternion
    target_scale = np.array([1, 1, 1], dtype=np.float32)

    test_matrix = np.eye(4, dtype=np.float32)

    result_matrix = np.empty((4, 4), dtype=np.float32)
    mat4.matrix_composition(
        target_translation,
        target_rotation,
        target_scale,
        result_matrix)

    np.testing.assert_array_almost_equal(test_matrix, result_matrix)


def test_matrix_composition_specific_case():
    test_translation = np.array([2, 3, 4], dtype=np.float32)
    test_rotation = np.array([-0.70710678118, 0, 0, 0.70710678118], dtype=np.float32)  # quaternion
    test_scale = np.array([5, 6, 7], dtype=np.float32)

    target_matrix = np.array([[5,  0, 0, 2],
                              [0,  0, 7, 3],
                              [0, -6, 0, 4],
                              [0,  0, 0, 1]], dtype=np.float32)

    result_matrix = np.empty((4, 4), dtype=np.float32)
    mat4.matrix_composition(
        test_translation,
        test_rotation,
        test_scale,
        result_matrix)

    np.testing.assert_array_almost_equal(target_matrix, result_matrix)


def test_matrix_decomposition_eye():

    target_translation = np.array([0, 0, 0], dtype=np.float32)
    target_rotation = np.array([0, 0, 0, 1], dtype=np.float32)  # quaternion
    target_scale = np.array([1, 1, 1], dtype=np.float32)

    test_matrix = np.eye(4, dtype=np.float32)

    result_translation = np.empty((3,), dtype=np.float32)
    result_rotation = np.empty((4,), dtype=np.float32)  # quaternion
    result_scale = np.empty((3,), dtype=np.float32)

    mat4.matrix_decomposition(
        test_matrix,
        result_translation,
        result_rotation,
        result_scale)

    np.testing.assert_array_equal(target_translation, result_translation)
    np.testing.assert_array_equal(target_rotation, result_rotation)
    np.testing.assert_array_equal(target_scale, result_scale)


def test_matrix_decomposition_case_1():

    target_translation = np.array([2, 3, 4], dtype=np.float32)
    target_rotation = np.array([-0.70710678118, 0, 0, 0.70710678118], dtype=np.float32)  # quaternion
    target_scale = np.array([5, 6, 7], dtype=np.float32)

    test_matrix = np.array([[5,  0, 0, 2],
                            [0,  0, 7, 3],
                            [0, -6, 0, 4],
                            [0,  0, 0, 1]], dtype=np.float32)

    result_translation = np.empty((3,), dtype=np.float32)
    result_rotation = np.empty((4,), dtype=np.float32)  # quaternion
    result_scale = np.empty((3,), dtype=np.float32)

    mat4.matrix_decomposition(
        test_matrix,
        result_translation,
        result_rotation,
        result_scale)

    np.testing.assert_array_equal(target_translation, result_translation)
    np.testing.assert_array_equal(target_rotation, result_rotation)
    np.testing.assert_array_equal(target_scale, result_scale)


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
