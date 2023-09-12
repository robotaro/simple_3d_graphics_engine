from ecs import constants
from ecs.editor import Editor

import os


def main():

    editor = Editor(window_title="Basic Scene Demo")

    editor.load_scene(scene_xml_fpath=os.path.join(constants.RESOURCES_DIR, "scenes", "default_scene.xml"))

    editor.run()

if __name__ == "__main__":
    main()
