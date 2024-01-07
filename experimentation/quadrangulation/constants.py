import numpy as np

BOTTOM_INDEX = 0
RIGHT_INDEX = 1
TOP_INDEX = 2
LEFT_INDEX = 3

CORNER_BOTTOM_RIGHT = 0
CORNER_TOP_RIGHT = 1
SIDE_TOP_LEFT = 2
CORNER_BOTTOM_LEFT = 3

MAP_OPPOSITE_SIDE = {
    TOP_INDEX: BOTTOM_INDEX,
    RIGHT_INDEX: LEFT_INDEX,
    BOTTOM_INDEX: TOP_INDEX,
    LEFT_INDEX: RIGHT_INDEX,
}

SIDES_ROTATION_0     = (BOTTOM_INDEX, RIGHT_INDEX, TOP_INDEX, LEFT_INDEX)
SIDES_ROTATION_90    = (LEFT_INDEX, BOTTOM_INDEX, RIGHT_INDEX, TOP_INDEX)
SIDES_ROTATION_180   = (TOP_INDEX, LEFT_INDEX, BOTTOM_INDEX, RIGHT_INDEX)
SIDES_ROTATION_270   = (RIGHT_INDEX, TOP_INDEX, LEFT_INDEX, BOTTOM_INDEX)
SIDES_ROTATION_TUPLE = (SIDES_ROTATION_0, SIDES_ROTATION_90, SIDES_ROTATION_180, SIDES_ROTATION_270)

INV_SIDES_ROTATION_0     = (RIGHT_INDEX, BOTTOM_INDEX, LEFT_INDEX, TOP_INDEX)
INV_SIDES_ROTATION_90    = (TOP_INDEX, RIGHT_INDEX, BOTTOM_INDEX, LEFT_INDEX)
INV_SIDES_ROTATION_180   = (LEFT_INDEX, TOP_INDEX, RIGHT_INDEX, BOTTOM_INDEX)
INV_SIDES_ROTATION_270   = (BOTTOM_INDEX, LEFT_INDEX, TOP_INDEX, RIGHT_INDEX)
INV_SIDES_ROTATION_TUPLE = (INV_SIDES_ROTATION_0, INV_SIDES_ROTATION_90, INV_SIDES_ROTATION_180, INV_SIDES_ROTATION_270)

SIDES_ORDERED = ((0, "not_inverted", *SIDES_ROTATION_0),
                 (90, "not_inverted", *SIDES_ROTATION_90),
                 (180, "not_inverted", *SIDES_ROTATION_180),
                 (270, "not_inverted", *SIDES_ROTATION_270),
                 (0, "inverted", *INV_SIDES_ROTATION_0),
                 (90, "inverted", *INV_SIDES_ROTATION_90),
                 (180, "inverted", *INV_SIDES_ROTATION_180),
                 (270, "inverted", *INV_SIDES_ROTATION_270),)

"""

Equation for pattern 0:
  |0|     |1|   |1|   |l0|
p0|1| + p1|0| + |1| = |l1|
  |0|     |1|   |1|   |l2|
  |1|     |0|   |1|   |l3|

equation for pattern 1:
  |0|     |1|     |0|     |1|   |2|    |1|   |l0|
p0|1| + p1|0| + p2|1| + p3|0| + |2| + x|1| = |l1|
  |0|     |1|     |0|     |1|   |1|    |0|   |l2|
  |1|     |0|     |1|     |0|   |1|    |0|   |l3|

equation for pattern 2:
  |0|     |1|     |0|     |1|   |3|    |1|    |1|   |l0|
p0|1| + p1|0| + p2|1| + p3|0| + |1| + x|1| + y|0| = |l1|
  |0|     |1|     |0|     |1|   |1|    |0|    |0|   |l2|
  |1|     |0|     |1|     |0|   |1|    |0|    |1|   |l3|
  
  equation for pattern 3:
  |0|     |1|     |0|     |1|     |1|   |3|    |2|   |l0|
p0|1| + p1|0| + p2|1| + p3|0| + q1|0| + |1| + x|0| = |l1|
  |0|     |1|     |0|     |1|     |1|   |1|    |0|   |l2|
  |1|     |0|     |1|     |0|     |0|   |1|    |0|   |l3|
  
equation for pattern 4:
  |0|     |1|     |0|     |1|     |1|   |4|    |2|    |1|   |l0|
p0|1| + p1|0| + p2|1| + p3|0| + q1|0| + |2| + x|0| + y|1| = |l1|
  |0|     |1|     |0|     |1|     |1|   |1|    |0|    |0|   |l2|
  |1|     |0|     |1|     |0|     |0|   |1|    |0|    |0|   |l3|
  
"""

PATTERN_0 = np.array([[0, 1, 1],
                      [1, 0, 1],
                      [0, 1, 1],
                      [1, 0, 1]], dtype=np.int32)

PATTERN_1 = np.array([[0, 1, 0, 1, 2, 1],
                      [1, 0, 1, 0, 2, 1],
                      [0, 1, 0, 1, 1, 0],
                      [1, 0, 1, 0, 1, 0]], dtype=np.int32)

PATTERN_2 = np.array([[0, 1, 0, 1, 3, 1, 1],
                      [1, 0, 1, 0, 1, 1, 0],
                      [0, 1, 0, 1, 1, 0, 0],
                      [1, 0, 1, 0, 1, 0, 1]], dtype=np.int32)

PATTERN_3 = np.array([[0, 1, 0, 1, 1, 3, 2],
                      [1, 0, 1, 0, 0, 1, 0],
                      [0, 1, 0, 1, 1, 1, 0],
                      [1, 0, 1, 0, 0, 1, 0]], dtype=np.int32)

PATTERN_4 = np.array([[0, 1, 0, 1, 1, 4, 2, 1],
                      [1, 0, 1, 0, 0, 2, 0, 1],
                      [0, 1, 0, 1, 1, 1, 0, 0],
                      [1, 0, 1, 0, 0, 1, 0, 0]], dtype=np.int32)

PATTERNS = (PATTERN_0, 
            PATTERN_1,
            PATTERN_2,
            PATTERN_3,
            PATTERN_4)

PATTERN_OFFSET_0 = np.array([-1, -1, -1, -1], dtype=np.int32).reshape(4, -1)
PATTERN_OFFSET_1 = np.array([-2, -2, -1, -1], dtype=np.int32).reshape(4, -1)
PATTERN_OFFSET_2 = np.array([-3, -1, -1, -1], dtype=np.int32).reshape(4, -1)
PATTERN_OFFSET_3 = np.array([-3, -1, -1, -1], dtype=np.int32).reshape(4, -1)
PATTERN_OFFSET_4 = np.array([-4, -2, -1, -1], dtype=np.int32).reshape(4, -1)

PATTERN_OFFSETS = (PATTERN_OFFSET_0,
                   PATTERN_OFFSET_1,
                   PATTERN_OFFSET_2,
                   PATTERN_OFFSET_3,
                   PATTERN_OFFSET_4)

"""
   [3]---[9]-------[8]---[2]
    |  5  |    4    |  3  |
  [10]---[15]-----[14]---[7]
    |     |         |     |
    |  6  |    8    |  2  |
    |     |         |     |
  [11]---[12]-----[13]---[6]
    |  7  |    0    |  1  |
   [0]---[4]-------[5]---[1]
                     
"""

SUBPATCH_CORNER_INDICES = {
  0: (4, 5, 13, 12),
  1: (5, 1, 6, 13),
  2: (13, 6, 7, 14),
  3: (14, 7, 2, 8),
  4: (15, 14, 8, 9),
  5: (10, 15, 9, 3),
  6: (11, 12, 15, 10),
  7: (0, 4, 12, 11),
  8: (12, 13, 14, 15),
}

PATCH_PERIMETER_EDGES_BY_CORNERS = {
  "bottom": {"subpatch_array_column": 0,
             "patch_corners": (0, 1),
             "subpatches":(7, 0, 1),
             "patch_vertices":(4, 5)},
  
  "right": {"subpatch_array_column": 1,
            "patch_corners": (1, 2),
            "subpatches":(1, 2, 3),
            "patch_vertices":(6, 7)},
  
  "top": {"subpatch_array_column": 2,
          "patch_corners": (2, 3),
          "subpatches":(3, 4, 5),
          "patch_vertices":(8, 9)},
  
  "left": {"subpatch_array_column": 3,
           "patch_corners": (3, 0),
           "subpatches":(5, 6, 7),
           "patch_vertices":(10, 11)}
}

SUBPATCH_INNER_CORNERS_EDGE_INTERSECTIONS = {
    12: ((4, 9), (11, 6)),
    13: ((5, 8), (11, 6)),
    14: ((4, 9), (10, 7)),
    15: ((5, 8), (10, 7)),
}

SUBPATCH_TL_AND_BR_MAP = {
  (5, 1): {"bottom": [7, 0, 1], "right": [3, 2, 1], "top": [5, 4, 3], "left": [5, 6, 7]},
  (5, 2): {"bottom": [6, 8, 2], "right": [3, 2],    "top": [5, 4, 3], "left": [5, 6]},
  (5, 0): {"bottom": [7, 0],    "right": [4, 8, 0], "top": [5, 4],    "left": [5, 6, 7]},
  (5, 8): {"bottom": [6, 8],    "right": [4, 8],    "top": [5, 4],    "left": [5, 6]},
  
  (4, 1): {"bottom": [0, 1],    "right": [3, 2, 1], "top": [4, 3],    "left": [4, 8, 0]},
  (4, 2): {"bottom": [8, 2],    "right": [3, 2],    "top": [4, 3],    "left": [4, 8]},
  (4, 0): {"bottom": [0],       "right": [4, 8, 0], "top": [4],       "left": [4, 8, 0]},
  (4, 8): {"bottom": [8],       "right": [4, 8],    "top": [4],       "left": [4, 8]},
  
  (6, 1): {"bottom": [7, 0, 1], "right": [2, 1],    "top": [6, 8, 2], "left": [6, 7]},
  (6, 2): {"bottom": [6, 8, 2], "right": [2],       "top": [6, 8, 2], "left": [6]},
  (6, 0): {"bottom": [7, 0],    "right": [8, 0],    "top": [6, 8],    "left": [6, 7]},
  (6, 8): {"bottom": [6, 8],    "right": [8],       "top": [6, 8],    "left": [6]},
  
  (8, 1): {"bottom": [0, 1],    "right": [2, 1],    "top": [8, 2],    "left": [8, 0]},
  (8, 2): {"bottom": [8, 2],    "right": [2],       "top": [8, 2],    "left": [8]},
  (8, 0): {"bottom": [0],       "right": [8, 0],    "top": [8],       "left": [8, 0]},
  (8, 8): {"bottom": [8],       "right": [8],       "top": [8],       "left": [8]},
}

PATCH_PERIMETER_VERTICES_FROM_SUBPATCH_SELECTION = {
  (5, 1): (0, 1, 2, 3),
  (5, 2): (11, 6, 2, 3),
  (5, 0): (0, 5, 8, 3),
  (5, 8): (11, 13, 8, 3),
  
  (4, 1): (4, 1, 2, 9),
  (4, 2): (12, 6, 2, 9),
  (4, 0): (4, 5, 8, 9),
  (4, 8): (12, 13, 8, 9),
  
  (6, 1): (0, 1, 7, 10),
  (6, 2): (11, 6, 7, 10),
  (6, 0): (0, 5, 14, 10),
  (6, 8): (11, 13, 14, 10),
  
  (8, 1): (4, 1, 7, 15),
  (8, 2): (12, 6, 7, 15),
  (8, 0): (4, 5, 14, 15),
  (8, 8): (12, 13, 14, 15)
}


SUBPATCH_LOCATION = np.array([
  (1, 0),
  (2, 0),
  (2, 1),
  (2, 2),
  (1, 2),
  (0, 2),
  (0, 1),
  (0, 0),
  (1, 1)],
  dtype=np.int32
)
SUBPATCH_TOP_LEFT_INDEX_SEQUENCE = [5, 4, 6, 8]
SUBPATCH_BOTTOM_RIGHT_INDEX_SEQUENCE = [1, 2, 0, 8]

SUBPATCH_INDEX_TABLE_2D = np.array([[5, 4, 3], [6, 8, 2], [7, 0, 1]], dtype=np.int32)

# Main vertices indices
C0 = 0
C1 = 1
C2 = 2
C3 = 3
V0 = 4
V1 = 5
V2 = 6
V3 = 7
V4 = 8
V5 = 9
V6 = 10
V7 = 11
V8 = 12

# Pattern 1 Edges
PATTERN_1_EDGES = {
    (C0, V0): [C0, V0],
    (V0, V2): [V0, V2],
    (V2, C3): [V2, C3],
    (C3, C0): [C3, C0],
    
    (V0, C1): [V0, C1],
    (C1, V1): [C1, V1],
    (V1, V2): [V1, V2],
    (V2, V0): [V2, V0],
    
    (V2, V1): [V2, V1],
    (V1, C2): [V1, C2],   
    (C2, C3): [C2, C3],
    (C3, V2): [C3, V2]
}

# Pattern 2 Edges
PATTERN_2_EDGES = {
    (C0, V0): [C0, V0],
    (V0, C2): [V0, C2],
    (C2, C3): [C2, C3],
    (C3, C0): [C3, C0],
    
    (V0, V1): [V0, V1],
    (V1, C1): [V1, C1],
    (C1, C2): [C1, C2],
    (C2, V0): [C1, C2],

}

# Pattern 1 Edges
PATTERN_4_EDGES = {
  (C0, V0): [C0, V0],
  (V0, V6): [V0, V2],
  (V6, C3): [V2, C3],
  (C3, C0): [C3, C0],
  
  (V0, V1): [V0, V1],
  (V1, V5): [V1, V5],
  (V5, V6): [V5, V6],
  (V6, V0): [V6, V0],

  (V1, V2): [V1, V2],
  (V2, V4): [V2, V4],   
  (V4, V5): [V4, V5],
  (V5, V1): [V5, V1],

  (V2, C1): [V2, C1],
  (C1, V3): [C1, V3],   
  (V3, V4): [V3, V4],
  (V4, V2): [V4, V2],

  (V6, V5): [V6, V5],
  (V5, C2): [V5, C2],   
  (C2, C3): [C2, C3],
  (C3, V6): [C3, V6],

  (V5, V4): [V5,V4],
  (V4, V3): [V4,V3],   
  (V3, C2): [V3,C2],
  (C2, V5): [C2,V5]
}


# =================================================================
#                       Generator Functions
# =================================================================

def generate_patch_perimeter_corners() -> dict:
  
  import json
  
  lookup_dict = {}
  for key_tuple in SUBPATCH_TL_AND_BR_MAP.keys():

    subpatches = SUBPATCH_TL_AND_BR_MAP[key_tuple]

    patch_perimeter_corners = [-1] * 4
    for side, subpatches in subpatches.items():
        
        if side == 'bottom':
            patch_perimeter_corners[0] = SUBPATCH_CORNER_INDICES[subpatches[0]][0]
            patch_perimeter_corners[1] = SUBPATCH_CORNER_INDICES[subpatches[-1]][1]

        if side == 'top':
            patch_perimeter_corners[2] = SUBPATCH_CORNER_INDICES[subpatches[-1]][2]
            patch_perimeter_corners[3] = SUBPATCH_CORNER_INDICES[subpatches[0]][3]
    
    lookup_dict[key_tuple] = tuple(patch_perimeter_corners)
  return lookup_dict
