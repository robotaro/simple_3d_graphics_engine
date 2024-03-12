import sys
import os

from src2.core import constants
from src2.core.engine import Engine


def main():

    xml_path = os.path.join(constants.ROOT_DIR, "demos", "new_format", "editor_setup.xml")
    app = Engine(log_level="debug")
    app.load_from_xml(xml_fpath=xml_path)
    app.run()


if __name__ == "__main__":
    main()
