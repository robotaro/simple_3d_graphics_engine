

from dataclasses import dataclass
from playground.new_quadrangulation.patch import Patch
from dataclasses import dataclass, field

@dataclass
class PatchPattern3(Patch):
    
    """_summary_

           v--q1
       C3-------------C2
       |\            /|
       | \          / |
       |  \        /  |
       |   \      /   |
       |    V3--V2    |
       |    |    |    |
       |    |    |    |
       |    |    |    |
       |    |    |    |
       C0---V0---V1---C1
       x--^    ^--q1 ^--x

    """

    @property
    def bottom(self):
        return self.p1 + self.p3 + 2 * self.x + 3
    
    @property
    def right(self):
        return self.p0 + self.p2 + 1
    
    @property
    def top(self):
        return self.p1 + self.p3 + 1
    
    @property
    def left(self):
        return self.p0 + self.p2 + 1
