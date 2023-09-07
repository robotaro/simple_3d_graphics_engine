from ecs import constants
from ecs.editor import Editor
from ecs.systems.render_system.font_library import FontLibrary

import os


def main():

    editor = Editor(
        window_size=constants.DEFAULT_EDITOR_WINDOW_SIZE,
        window_title="Basic Scene Demo"
    )

    editor.create_system(system_type="input_control_system")
    editor.create_system(system_type="render_system")
    editor.create_system(system_type="imgui_system")

    editor.load_scene(scene_xml_fpath=os.path.join(constants.RESOURCES_DIR,"scenes", "default_scene.xml"))

    editor.run()

if __name__ == "__main__":
    main()
