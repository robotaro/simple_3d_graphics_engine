import sys
import os

from src2.core.app import App


def main():

    xml_path = r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\demos\new_format\editor_setup.xml"
    app = App(log_level="debug")
    app.load_from_xml(xml_fpath=xml_path)
    app.run()


if __name__ == "__main__":
    main()
