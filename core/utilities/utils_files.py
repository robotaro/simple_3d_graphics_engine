import os
from typing import Union


def list_filenames(directory: str, selected_extension: Union[str, None] = None) -> list:

    if not isinstance(directory, str):
        raise TypeError('[ERROR] Input directory must be a string')

    if not os.path.isdir(directory):
        raise TypeError(f'[ERROR] Input directory is not a valid directory: {directory}')

    items = os.listdir(directory)
    folder_names = [item for item in items if os.path.isdir(os.path.join(directory, item))]
    filenames = [item for item in items if os.path.isfile(os.path.join(directory, item))]

    if selected_extension is not None:
        extension = selected_extension.strip('.')
        filenames = [f"{filename}.{extension}" for filename in filenames]

    # TODO: Add recursive option. Maybe as a new function

    return filenames
