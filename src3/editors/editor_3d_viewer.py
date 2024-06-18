
from src3.editors.editor import Editor


class Editor3DViewer(Editor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, elapsed_time: float):
        pass

    def handle_event_keyboard_press(self, event_data: tuple):
        print(event_data)

    