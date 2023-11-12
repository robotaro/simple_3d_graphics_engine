from dataclasses import dataclass
import numpy as np


class DataBlock:

    """
    This is the building block (pun intended) to all large data manipulation, in and out of rendering.
    A contiguous data array of heterogeneous type that can be dumped to an HDF5 file
    """

    __slots__ = [
        "metadata",
        "data",
        "data_format"
    ]

    def __init__(self, data_format: str, data_shape: tuple, data_type: type, metadata=None):
        self.metadata = {} if metadata is None else metadata
        self.data = np.empty(data_shape, dtype=data_type)
        self.data_format = data_format
