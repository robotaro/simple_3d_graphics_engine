from dataclasses import dataclass
from experimentation.quadrangulation.patch import Patch
from dataclasses import dataclass, field


class PatchPattern4(Patch):
    
    """
                v--q1
       C3-----------------C2
       | \              _/ |
       |  \     5     _/   |
       |   \        _/     | <--y
       |    \      /       |
       |     V6--V5    4   V3
       |  0  |    |\_    _/|
       |     |    |  \  /  |
       |     | 1  |   V4   |
       |     |    | 2 |  3 |
       C0---V0---V1---V2---C1
      x--^  q1--^ y--^    ^--x

    """
    
    def __init__(self):
        super().__init__()
        self._pattern = 4

    @property
    def bottom(self):
        return self.p1 + self.p3 + 2 * self.x + self.y + 4
    
    @property
    def right(self):
        return self.p0 + self.p2 + self.y + 2
    
    @property
    def top(self):
        return self.p1 + self.p3 + 1
    
    @property
    def left(self):
        return self.p0 + self.p2 + 1
    
    # =================================================================
    #                        Core functions
    # =================================================================
    
    def calculate_pattern_main_vertices(self) -> dict:
        g = 0
