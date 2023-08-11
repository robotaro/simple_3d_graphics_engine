import numpy as np

from core.math import mat4

# For testing
from pyrr import Matrix44


def test_look_at():


    target = Matrix44.look_at(
        eye=(47.697, -8.147, 24.498),
        target=(0.0, 0.0, 8.0),
        up=(0.0, 1.0, 0.0),
        dtype=np.float32)

    result = mat4.look_at(position=np.array((47.697, -8.147, 24.498), dtype=np.float32),
                          target=np.array((0.0, 0.0, 8.0), dtype=np.float32),
                          up=np.array((0.0, 1.0, 0.0), dtype=np.float32))

    np.testing.assert_almost_equal(target.T, result)
