from dataclasses import dataclass
from playground.new_quadrangulation.patch import Patch
from dataclasses import dataclass, field

@dataclass
class PatchPattern1(Patch):
    
    """
        C3--------C2
        |\        |
        | \       | <--x
        |  \      |
        |   \     |
        |    V2---V1
        |    |    |
        |    |    |
        |    |    |
        |    |    |
        C0---V0---C1
           ^--x
        
    """

    @property
    def bottom(self):
        return self.p1 + self.p3 + self.x + 1
    
    @property
    def right(self):
        return self.p0 + self.p2 + self.x + 1
    
    @property
    def top(self):
        return self.p1 + self.p3 + 1
    
    @property
    def left(self):
        return self.p0 + self.p2 + 1
    
    def increase_x(self, step_size: int) -> None:
        pass
    
    def decrease_x(self, step_size: int) -> None:
        pass
