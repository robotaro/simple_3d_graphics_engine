

from dataclasses import dataclass
from playground.new_quadrangulation.patch import Patch
from dataclasses import dataclass, field

@dataclass
class PatchPattern2(Patch):
    
    """

        C3-------------C2
        |            _/|
        |          _/  |
   y--> |        _/    | <--x
        |      _/      |
        |     /        |
        C0---V0---V1---C1
        x--^    ^--y

    """

    @property
    def bottom(self):
        return self.p1 + self.p3 + self.x + self.y + 3
    
    @property
    def right(self):
        return self.p0 + self.p2 + self.x + 1
    
    @property
    def top(self):
        return self.p1 + self.p3 + 1
    
    @property
    def left(self):
        return self.p0 + self.p2 + self.x + 1
