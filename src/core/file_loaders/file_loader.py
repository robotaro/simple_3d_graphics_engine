from abc import ABC, abstractmethod


class FileLoader(ABC):

    __slots__ = [
        "external_data_groups"]

    def __init__(self, all_resources: dict):
        self.external_data_groups = all_resources

    @abstractmethod
    def load(self, resource_uid: str, fpath: str) -> bool:
        return True