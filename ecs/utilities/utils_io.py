import os


def list_filepaths(directory: str, extension: str):

    extension = f".{extension.strip('.')}"

    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                filepaths.append(relative_path)

    return filepaths