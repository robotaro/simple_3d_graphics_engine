from ecs import constants
from ecs.editor import Editor
from ecs.systems.render_system.font import Font

import os


def main():

    editor = Editor(
        window_size=(1024, 768),
        window_title="Basic Scene Demo"
    )

    font = Font()
    font.load(ttf_fpath=os.path.join(constants.FONTS_DIR, "Consolas.ttf"))

    editor.create_system(system_type="render_system",
                         subscribed_events=[
                             constants.EVENT_MOUSE_BUTTON_PRESS,
                             constants.EVENT_KEYBOARD_PRESS,
                         ])
    #editor.create_system(system_type="imgui_system",
    #                     subscribed_events=[constants.EVENT_MOUSE_SCROLL])
    editor.create_system(system_type="input_control_system",
                         subscribed_events=[
                             constants.EVENT_MOUSE_SCROLL,
                             constants.EVENT_MOUSE_MOVE,
                             constants.EVENT_KEYBOARD_PRESS,
                             constants.EVENT_KEYBOARD_RELEASE,
                         ])

    # Create camera
    camera_uid = editor.component_pool.create_entity(name="camera")
    editor.add_component(
        entity_uid=camera_uid,
        component_type=constants.COMPONENT_TYPE_CAMERA,
        viewport=(0, 0, 1024, 768))
    editor.add_component(
        entity_uid=camera_uid,
        component_type=constants.COMPONENT_TYPE_TRANSFORM_3D,
        position=(0, 0, -2))
    editor.add_component(
        entity_uid=camera_uid,
        component_type=constants.COMPONENT_TYPE_INPUT_CONTROL)

    dragon_fpath = r"D:\git_repositories\alexandrepv\simple_3d_graphics_enigne\resources\models\dragon.obj"

    # Dragon #1
    dragon_1_uid = editor.component_pool.create_entity(name="dragon_1")
    editor.add_component(
        entity_uid=dragon_1_uid,
        component_type=constants.COMPONENT_TYPE_TRANSFORM_3D)
    editor.add_component(
        entity_uid=dragon_1_uid,
        component_type=constants.COMPONENT_TYPE_MESH,
        shape=constants.MESH_SHAPE_FROM_OBJ,
        fpath=dragon_fpath)
    editor.add_component(
        entity_uid=dragon_1_uid,
        component_type=constants.COMPONENT_TYPE_RENDERABLE)

    # Dragon #2
    dragon_2_uid = editor.component_pool.create_entity(name="dragon_2")
    editor.add_component(
        entity_uid=dragon_2_uid,
        component_type=constants.COMPONENT_TYPE_TRANSFORM_3D,
        position=(-1, 0, -1))
    editor.add_component(
        entity_uid=dragon_2_uid,
        component_type=constants.COMPONENT_TYPE_MESH,
        shape=constants.MESH_SHAPE_FROM_OBJ,
        fpath=dragon_fpath)
    editor.add_component(
        entity_uid=dragon_2_uid,
        component_type=constants.COMPONENT_TYPE_RENDERABLE)

    editor.run()


if __name__ == "__main__":
    main()
