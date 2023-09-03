from ecs import constants
from ecs.editor import Editor
from ecs.systems.render_system.font_library import FontLibrary

import os


def main():

    editor = Editor(
        window_size=(1600, 900),
        window_title="Basic Scene Demo"
    )

    editor.create_system(system_type="input_control_system")
    editor.create_system(system_type="render_system")
    editor.create_system(system_type="imgui_system")

    editor.load_scene(scene_xml_fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\scenes\default_scene.xml")

    editor.run()

if __name__ == "__main__":
    main()
