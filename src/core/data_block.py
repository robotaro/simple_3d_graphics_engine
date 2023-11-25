from dataclasses import dataclass
import numpy as np


class DataBlock:

    """
    This is the building block to all large data manipulation, in and out of rendering.
    A contiguous data array of heterogeneous type that can be dumped to an HDF5 file
    """

    __slots__ = [
        "metadata",
        "data",
        "format"
    ]

    def __init__(self, data_shape: tuple, data_type: type, data_format: str, metadata=None):
        self.metadata = {} if metadata is None else metadata
        self.data = np.empty(data_shape, dtype=data_type)
        self.format = data_format  # Format of the data stored, like vec3, vec4, etc
