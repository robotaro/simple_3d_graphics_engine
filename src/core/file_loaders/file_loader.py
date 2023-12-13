from abc import ABC, abstractmethod


class FileLoader(ABC):

    __slots__ = [
        "all_resources"]

    def __init__(self, all_resources: dict):
        self.all_resources = all_resources

    @abstractmethod
    def load(self, resource_uid: str, fpath: str) -> bool:
        return True