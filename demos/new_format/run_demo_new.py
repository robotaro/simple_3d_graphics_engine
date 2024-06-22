import sys
import os

from src2.core import constants
from src2.core.engine import Engine


def main():

    xml_path = os.path.join(constants.ROOT_DIR, "demos", "new_format", "editor_setup.xml")
    engine = Engine(log_level="debug")

    #scene = engine.create_scene(name="main_scene")

    engine.run()


if __name__ == "__main__":
    main()
