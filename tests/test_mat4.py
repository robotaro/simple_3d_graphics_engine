import numpy as np

from ecs.math import mat4


def test_orthographic_projection():

    # Example came from ChatGPT, so make look for a more reliable source
    target = np.array(
        [[ 0.1       ,  0.        ,  0.        ,  0.        ],
         [ 0.        ,  0.2       ,  0.        ,  0.        ],
         [ 0.        ,  0.        , -0.02020202, -1.020202  ],
         [ 0.        ,  0.        ,  0.        ,  1.        ]])

    result = mat4.orthographic_projection(
        left=-10,
        right=10,
        bottom=-5,
        top=5,
        near=1,
        far=100
    )

    np.testing.assert_almost_equal(target, result)
