from ecs import constants
from ecs.editor import Editor
from ecs.systems.render_system.font_library import FontLibrary

import os


def main():

    editor = Editor(
        window_size=(1024, 768),
        window_title="Basic Scene Demo"
    )

    editor.create_system(system_type="render_system",
                         subscribed_events=[
                             constants.EVENT_MOUSE_BUTTON_PRESS,
                             constants.EVENT_KEYBOARD_PRESS,
                             constants.EVENT_WINDOW_RESIZE,
                         ])
    editor.create_system(system_type="imgui_system")
    editor.create_system(system_type="input_control_system",
                         subscribed_events=[
                             constants.EVENT_MOUSE_SCROLL,
                             constants.EVENT_MOUSE_MOVE,
                             constants.EVENT_KEYBOARD_PRESS,
                             constants.EVENT_KEYBOARD_RELEASE,
                         ])

    editor.load_scene(scene_xml_fpath=r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\scenes\default_scene.xml")

    editor.run()

if __name__ == "__main__":
    main()
