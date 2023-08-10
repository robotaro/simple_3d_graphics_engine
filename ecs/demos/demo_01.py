import os
import time
import logging

import numpy as np

from ecs import constants
from ecs.editor import Editor
from ecs.systems.render_system.render_system import RenderSystem


def main():

    editor = Editor(
        window_size=(1024, 768),
        window_title="Basic Scene Demo",
        vertical_sync=True
    )

    render_system = RenderSystem()

    editor.register_system(name="render_system",
                           system=render_system,
                           subscribed_events=[
                               constants.EVENT_MOUSE_MOVE
                           ])
    editor.run()


if __name__ == "__main__":
    main()
