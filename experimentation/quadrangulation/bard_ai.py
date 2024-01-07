import numpy as np
from typing import List, Tuple

# Code translated from: https://www.particleincell.com/2012/quad-interpolation/ using Bing AI

def map_square_to_quad(quad: List[Tuple[float, float]], points: np.ndarray) -> np.ndarray:
    """
    Maps points from a unit square to an arbitrary quadrilateral using bilinear interpolation.

    :param quad: A list of 4 tuples representing the coordinates of the destination quadrilateral.
    :param points: An (N, 2) array of points located on the unit square.
    :return: An (N, 2) array of the transformed points on the destination quadrilateral.
    """
    x = quad[:, 0]
    y = quad[:, 1]
    X = points[:, 0]
    Y = points[:, 1]

    # compute coefficients for the transformation
    div = (x[0]-x[1]+x[2]-x[3])*(y[0]-y[1]+y[2]-y[3])-(x[0]-x[1]+x[2]-x[3])**2
    a = (x[0]*y[1]-x[1]*y[0]+x[1]*y[3]-x[3]*y[1]+x[3]*y[2]-x[2]*y[3])/div
    b = (x[0]*y[2]-x[2]*y[0]+x[1]*y[2]-x[2]*y[1]+x[3]*y[0]-x[0]*y[3])/div
    c = x[3]-x[0]+a*x[3]
    d = x[2]-x[0]+b*x[2]
    e = y[3]-y[0]+a*y[3]
    f = y[2]-y[0]+b*y[2]

    # compute the mapped points
    den = 1/(a*X*Y+b*X+c*Y+d)
    x_out = (X*(e*Y+f)+c*(e*Y+f)+a*X*(d*Y+e))/(a*X*Y+b*X+c*Y+d)
    y_out = (Y*(c*X+d)+b*(e*Y+f)+a*Y*(d*Y+e))/(a*X*Y+b*X+c*Y+d)

    return np.column_stack((x_out, y_out))

# Example usage
quad = np.array([(2.5, 2.5), (4.5, 2.5), (5.5, 5.5), (2.5, 5.5)])
points = np.array([[.5,.5],[.75,.75]])
print(map_square_to_quad(quad, points))