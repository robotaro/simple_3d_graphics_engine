class Entity:

    __slots__ = [
        "name",
        "root_parent_uid",
        "parent_uid",
        "children_uids",
        "system_owned"
    ]

    def __init__(self, name="", parent=None, system_owned=False):
        self.name = name
        self.root_parent_uid = None  # TODO: This should be filled during initialisation, or when the entity tree is modified
        self.parent_uid = parent
        self.children_uids = []
        self.system_owned = system_owned

    @property
    def has_parent(self):
        return self.parent_uid is not None
