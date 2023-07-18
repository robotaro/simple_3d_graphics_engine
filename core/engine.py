import moderngl as mgl
from core import constants
from numba import njit


@njit
def blah_func(a, b, output):
    output = constants.FACE_NORMALS * a + b


if __name__ == "__main__":
    a = 1
    b = 2
    c = 0
    blah_func(a, b, c)
    g = 0


