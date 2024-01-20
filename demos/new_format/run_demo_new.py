import sys
import os

from src2.core.editor import Editor


def main():

    editor = Editor(window_title="Basic Scene Demo", vertical_sync=False)

    editor.load_from_xml(xml_fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_engine\demos\new_format\editor_setup.xml")

    editor.run(profiling_enabled=False)


if __name__ == "__main__":
    main()
