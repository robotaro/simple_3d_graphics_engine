import numpy as np

# PATCH ADJACENT INDICES - KEEP THIS ORDER!
PATCH_TOP_EDGE = 0
PATCH_RIGHT_EDGE = 1
PATCH_BOTTOM_EDGE = 2
PATCH_LEFT_EDGE = 3
PATCH_EDGE_LIST = [PATCH_TOP_EDGE,
                   PATCH_RIGHT_EDGE,
                   PATCH_BOTTOM_EDGE,
                   PATCH_LEFT_EDGE]

PATCH_TOP_RIGHT_CORNER = 0
PATCH_BOTTON_RIGHT_CORNER = 1
PATCH_BOTTOM_LEFT_CORNER = 2
PATCH_TOP_LEFT_CORNER = 3
PATCH_CORNER_AFFECTED_EDGES_MAP = np.array([[0, 1],  # (edge_0, edge_1)
                                            [1, 2],
                                            [2, 3],
                                            [3, 0]], dtype=np.int32)
PATCH_CORNER_COORDS = np.array([[0, 3],  # (row, col)
                                [3, 3],
                                [3, 0],
                                [0, 0]], dtype=np.int32)

CORNER_TO_EDGE_CW = np.array([0, 1, 2, 3], dtype=np.int32)  # index: Corner ID, data: Edge IDs
CORNER_TO_EDGE_CCW = np.array([1, 2, 3, 0], dtype=np.int32)  # index: Corner ID, data: Edge IDs
EDGE_TO_CORNER_CW = np.array([3, 0, 1, 2], dtype=np.int32)  # index: Edge ID, data: Corner IDs
EDGE_TO_CORNER_CCW = np.array([0, 1, 2, 3], dtype=np.int32)  # index: Edge ID, data: Corner IDs

PATCH_EDGE_OPPOSITE_MAP = np.zeros((max(PATCH_EDGE_LIST) + 1,), dtype=np.int32)
PATCH_EDGE_OPPOSITE_MAP[PATCH_TOP_EDGE] = PATCH_BOTTOM_EDGE
PATCH_EDGE_OPPOSITE_MAP[PATCH_RIGHT_EDGE] = PATCH_LEFT_EDGE
PATCH_EDGE_OPPOSITE_MAP[PATCH_BOTTOM_EDGE] = PATCH_TOP_EDGE
PATCH_EDGE_OPPOSITE_MAP[PATCH_LEFT_EDGE] = PATCH_RIGHT_EDGE

# Bezier coefficients
BEZIER_COEFFS = np.array([[-1,  3, -3, 1],
                          [ 3, -6,  3, 0],
                          [-3,  3,  0, 0],
                          [ 1,  0,  0, 0]], dtype=np.float32)

BEZIER_TWIST_UP_VECTOR_X_AXIS = np.array([1, 0, 0], dtype=np.float32)
BEZIER_TWIST_UP_VECTOR_Y_AXIS = np.array([0, 1, 0], dtype=np.float32)
BEZIER_TWIST_UP_VECTOR_Z_AXIS = np.array([0, 0, 1], dtype=np.float32)
MAX_CONNECTED_PATCHES_PER_CORNER = 5