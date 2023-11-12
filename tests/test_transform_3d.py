from scipy.spatial.transform import Rotation as R
from pytest import fixture
import numpy as np
from src.components.transform_3d import Transform3D
from src.math import mat4

@fixture
def condition_0_parameters():
    return {
        "position": "0 0 0",
        "rotation": "0 0 0",
        "scale": "1",
        "mode": "euler_xyz",
        "degrees": "true"
    }

@fixture
def condition_1_parameters():
    return {
        "position": "1 2 3",
        "rotation": "0 45 0",
        "scale": "1",
        "mode": "euler_xyz",
        "degrees": "true"
    }


@fixture
def condition_2_parameters():
    return {
        "position": "1 2 3",
        "rotation": "45 45 0",
        "scale": "1",
        "mode": "euler_xyz",
        "degrees": "true"
    }


def test_parameter_position(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    assert transform.position == (1.0, 2.0, 3.0)


def test_parameter_rotation(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    assert transform.rotation == (0.0, 0.7853981633974475, 0.0)


def test_parameter_mode(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    assert transform.mode == "euler_xyz"


def test_parameter_degrees(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    assert transform.degrees


def test_constructor_local_matrix(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    target = np.eye(4, dtype=np.float32)
    np.testing.assert_array_equal(target, transform.local_matrix)


def test_constructor_world_matrix(condition_1_parameters):
    transform = Transform3D(parameters=condition_1_parameters)
    target = np.eye(4, dtype=np.float32)
    np.testing.assert_array_equal(target, transform.world_matrix)


def test_update_input_values_euler_xyz(condition_2_parameters):
    transform = Transform3D(parameters=condition_2_parameters)
    transform.update()

    euler_angles = transform.rotation
    rotation = R.from_euler('xyz', euler_angles)
    target = np.eye(4, dtype=np.float32)
    target[:3, :3] = rotation.as_matrix().astype(np.float32)
    target[:3, 3] = transform.position

    np.testing.assert_array_almost_equal(target, transform.local_matrix)


def test_update_local_matrix_euler_xyz(condition_0_parameters):
    transform = Transform3D(parameters=condition_0_parameters)

    # These values should be overwritten because local matrix update takes precedence
    transform.position = (4, 5, 6)
    transform.rotation = (10, 20, 30)
    transform.scale = 2
    transform.input_values_updated = True



    transform.local_matrix = np.array([[0.707107, 0., 0.707107,  1.],
                                       [0., 1., 0.,              2.],
                                       [-0.707107, 0., 0.707107, 3.],
                                       [0., 0., 0.,              1.]], dtype=np.float32)
    transform.local_matrix_updated = True

    transform.update()

    assert transform.position == (1.0, 2.0, 3.0)
    #assert transform.position == (0.0, 0.7853981633974475, 0.0)
    #assert transform.position == 1.0



