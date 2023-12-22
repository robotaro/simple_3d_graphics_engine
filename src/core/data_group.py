class DataGroup:

    __slots__ = [
        "archetype",
        "data_blocks",
        "metadata"
    ]

    def __init__(self, archetype="general", metadata=None):
        self.archetype = archetype
        self.data_blocks = {}
        self.metadata = {} if metadata is None else metadata
