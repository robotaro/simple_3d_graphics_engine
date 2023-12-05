import numpy as np
import h5py


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

    def __init__(self, data: np.ndarray, metadata=None, copy_data=True):
        self.metadata = {} if metadata is None else metadata
        self.data = data.copy() if copy_data else data

    def save_to_hdf5(self, hdf5_group: h5py.Group):
        if self.data is None:
            raise ValueError("DataBlock data has not been initialized")

        # Create a dataset within the provided HDF5 group
        dataset = hdf5_group.create_dataset(self.data.dtype, data=self.data)

        # Add metadata as attributes to the HDF5 dataset
        for key, value in self.metadata.items():
            dataset.attrs[key] = value

    @classmethod
    def load_from_hdf5(cls, hdf5_dataset: h5py.Dataset):
        # Load data from the HDF5 dataset
        data = hdf5_dataset[...]

        # Load metadata from the HDF5 dataset attributes
        metadata = {key: hdf5_dataset.attrs[key] for key in hdf5_dataset.attrs}

        # Create a new DataBlock instance with the loaded data and metadata
        return cls(data, metadata, copy_data=False)