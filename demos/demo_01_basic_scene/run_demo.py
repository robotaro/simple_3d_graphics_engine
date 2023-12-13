import sys
import os


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)

from src.core.editor import Editor
def main():

    editor = Editor(window_title="Basic Scene Demo", vertical_sync=False)

    editor.load_scene_from_xml(scene_xml_fpath="demos/demo_01_basic_scene/basic_scene.xml")

    editor.run(profiling_enabled=False)


if __name__ == "__main__":
    main()
