import sys
import os

from src2.core.app import App


def main():

    app = App(window_title="Basic Scene Demo", vertical_sync=False)
    app.load_from_xml(xml_fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\demos\new_format\editor_setup.xml")
    app.run()


if __name__ == "__main__":
    main()
