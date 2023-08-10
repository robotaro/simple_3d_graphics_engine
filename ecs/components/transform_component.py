import numpy as np


class Transform:

    def __init__(self):
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.local_matrix = np.eye(4, dtype=np.float32)
        self.position = np.zeros((3,), dtype=np.float32)
        self.rotation = np.zeros((3,), dtype=np.float32)
        self.scale = np.ones((3,), dtype=np.float32)
