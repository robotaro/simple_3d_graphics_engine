import os
from src import constants


def validate_resource_filepath(fpath: str) -> str:
    """
    Returns the absolute filepath after checking if that fpath is not a relative path already stored in
    the resources folder

    :param fpath: str, relative or absolute filepath
    :return:
    """

    valid_fpath = fpath.replace("\\", os.sep).replace("/", os.sep).strip(os.sep)

    absolute_fpath = os.path.join(constants.RESOURCES_DIR, valid_fpath)
    if os.path.isfile(absolute_fpath):
        return absolute_fpath

    return fpath


def list_filepaths(directory: str, extension: str):

    extension = f".{extension.strip('.')}"

    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                filepaths.append(relative_path)

    return filepaths