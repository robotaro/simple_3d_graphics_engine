import sys
import os

from src2.core.editor import Editor


def main():

    editor = Editor(window_title="Basic Scene Demo", vertical_sync=False)

    editor.load_scene_from_xml(scene_xml_fpath="demos/demo_01_basic_scene/basic_scene.xml")

    editor.run(profiling_enabled=False)


if __name__ == "__main__":
    main()
