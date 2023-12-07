class Resource:

    __slots__ = [
        "resource_type",
        "data_blocks",
        "metadata"
    ]

    def __init__(self, resource_type: str, metadata=None):
        self.resource_type = resource_type
        self.data_blocks = {}
        self.metadata = {} if metadata is None else metadata
