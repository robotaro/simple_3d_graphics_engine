from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from playground.new_quadrangulation.patch import Patch
from dataclasses import dataclass, field
import numpy as np

@dataclass
class PatchPattern0(Patch):
    
    # TODO: Check if Pattern 0 is for 1x1 only!
    
    """
    C3----C2
    |      |
    |      |
    C0----C1
    """
    
    @property
    def bottom(self):
        return self.p1 + self.p3 + 1
    
    @property
    def right(self):
        return self.p0 + self.p2 + 1
    
    @property
    def top(self):
        return self.p1 + self.p3 + 1
    
    @property
    def left(self):
        return self.p0 + self.p2 + 1
    
    def tesselate_pattern(self):
        
        vertices = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
        edges = np.array([(0, 1), (1, 2), (2, 3), (3, 0)], dtype=np.int32)
        
        # TODO: Complete
        
        return super().tesselate_pattern()
    
