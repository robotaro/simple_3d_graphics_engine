import argparse

# Demos
from demos import demo_01_window
from demos import demo_02_gltf


def main():

    # Parse all input arguments
    parser = argparse.ArgumentParser(description='Graphics Engine Demo')
    parser.add_argument("name",
                        type=str,
                        default='demo_01')
    args, unknown_args = parser.parse_known_args()

    # Store every demo in a dictionary for easy access
    demos = {
        'demo_01': demo_01_cube.run,
        'demo_02': demo_02_gltf.run
    }

    # Safety check
    if args.name not in demos:
        raise ValueError(f"[ERROR] Demo name '{args.name}' not implemented.")

    # Run Demo
    demos[args.name]()


if __name__ == "__main__":
    main()
