from src.core import constants

# Default system subscribed events
SUBSCRIBED_EVENTS_RENDER_SYSTEM = [
    constants.EVENT_ENTITY_SELECTED,
    constants.EVENT_MOUSE_ENTER_UI,
    constants.EVENT_MOUSE_LEAVE_UI,
    constants.EVENT_MOUSE_ENTER_GIZMO_3D,
    constants.EVENT_MOUSE_LEAVE_GIZMO_3D,
    constants.EVENT_MOUSE_BUTTON_PRESS,
    constants.EVENT_KEYBOARD_PRESS,
    constants.EVENT_WINDOW_FRAMEBUFFER_SIZE]

SUBSCRIBED_EVENTS_IMGUI_SYSTEM = [
    constants.EVENT_ENTITY_SELECTED,
    constants.EVENT_KEYBOARD_PRESS,
    constants.EVENT_PROFILING_SYSTEM_PERIODS]

SUBSCRIBED_EVENTS_INPUT_CONTROL_SYSTEM = [
    constants.EVENT_MOUSE_SCROLL,
    constants.EVENT_MOUSE_MOVE,
    constants.EVENT_KEYBOARD_PRESS,
    constants.EVENT_KEYBOARD_RELEASE]

SUBSCRIBED_EVENTS_GIZMO_3D_SYSTEM = [
    constants.EVENT_MOUSE_SCROLL,
    constants.EVENT_MOUSE_BUTTON_PRESS,
    constants.EVENT_MOUSE_BUTTON_RELEASE,
    constants.EVENT_MOUSE_MOVE,
    constants.EVENT_KEYBOARD_PRESS,
    constants.EVENT_KEYBOARD_RELEASE,
    constants.EVENT_ENTITY_SELECTED,
    constants.EVENT_ENTITY_DESELECTED,
    constants.EVENT_MOUSE_ENTER_UI,
    constants.EVENT_MOUSE_LEAVE_UI,
    constants.EVENT_GIZMO_3D_SYSTEM_PARAMETER_UPDATED
]

SUBSCRIBED_EVENTS_TRANSFORM_SYSTEM = []

SUBSCRIBED_EVENTS_IMPORT_SYSTEM = [
    constants.EVENT_WINDOW_DROP_FILES]

SYSTEMS_EVENT_SUBSCRITONS = {
    constants.SYSTEM_NAME_RENDER: SUBSCRIBED_EVENTS_RENDER_SYSTEM,
    constants.SYSTEM_NAME_IMGUI: SUBSCRIBED_EVENTS_IMGUI_SYSTEM,
    constants.SYSTEM_NAME_INPUT_CONTROL: SUBSCRIBED_EVENTS_INPUT_CONTROL_SYSTEM,
    constants.SYSTEM_NAME_GIZMO_3D: SUBSCRIBED_EVENTS_GIZMO_3D_SYSTEM,
    constants.SYSTEM_NAME_TRANSFORM: SUBSCRIBED_EVENTS_TRANSFORM_SYSTEM,
    constants.SYSTEM_NAME_IMPORT: SUBSCRIBED_EVENTS_IMPORT_SYSTEM
}