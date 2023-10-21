from src.math import mat4
import time
import numpy as np

def main():

    count = 100000

    position = np.array((1, 2, 3), dtype=np.float32)
    rotation = np.array((0.3, 1.2, .76), dtype=np.float32)
    scale = 2

    t0 = time.perf_counter()
    for i in range(count):
        transform1 = mat4.compute_transform(position=position, rotation_rad=rotation, scale=scale)
    t1 = time.perf_counter()
    print(f"Normal = {t1-t0:.3f} seconds")

    t0 = time.perf_counter()
    for i in range(count):
        transform2 = mat4.create_transform_xyz(position=position, rotation=rotation, scale=scale)
    t1 = time.perf_counter()
    print(f"Numba = {t1-t0:.3f} seconds")

    print(transform1)
    print(transform2)



if __name__ == "__main__":
    main()