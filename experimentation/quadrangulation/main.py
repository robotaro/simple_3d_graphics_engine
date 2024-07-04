import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np

from experimentation.quadrangulation.patch_pattern_4 import PatchPattern4
from numba import njit


def demo():
  
    a = (1.0, 3.0, 4)
    b = (2.0, 4.0, 4)



    corners = np.array([(0, 0),
                      (1, 0),
                      (1, 1),
                      (0, 1)],
                     dtype=np.float32)

    patch = PatchPattern4(
    patch_corners=corners,
    bottom=16,
    right=5,
    top=5,
    left=4
    )

    patch.process()
  
 
  
    #patch.shift_right(step_size=2)
    #patch.shift_down(step_size=1)

    patch.show_subpatches()

    g = 0
  


if __name__ == "__main__":
    demo()
    
"""

def main():
    
  # Order (North, East, South, West)
  sides = (4, 16, 5, 5)
  pattern = find_pattern(n_sides=sides)

  c = -np.array([0, 1])
  A = np.array([[-1, 1], [3, 2], [2, 3]])
  b_u = np.array([1, 12, 12])
  b_l = np.full_like(b_u, -np.inf)

  constraints = LinearConstraint(A, b_l, b_u)
  integrality = np.ones_like(c)
  t0 = time.perf_counter()
  res = milp(c=c, constraints=constraints, integrality=integrality)
  t1 = time.perf_counter()
  print((t1-t0)    * 1000.0)
  print(res)

  c = [-1, 4]
  A = [[-3, 1], [1, 2]]
  b = [6, 4]
  x0_bounds = (None, None)
  x1_bounds = (-3, None)
  t0 = time.perf_counter()
  res = linprog(c, A_ub=A, b_ub=b, bounds=[x0_bounds, x1_bounds])
  t1 = time.perf_counter()
  res.fun
  print((t1-t0) * 1000.0)
  print(res)

"""