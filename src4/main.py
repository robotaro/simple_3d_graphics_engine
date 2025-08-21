
# main.py
"""Main entry point"""
import moderngl_window as mglw
from src4.ecs_editor import ECSEditor


def main():
    """Run the ECS editor"""
    mglw.run_window_config(ECSEditor)


if __name__ == "__main__":
    main()