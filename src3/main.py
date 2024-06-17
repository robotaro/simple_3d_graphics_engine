import sys
import os


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)

from src3.editor import Editor


def main():

    editor = Editor(window_title="Basic Scene Demo", vertical_sync=False)
    editor.run(profiling_enabled=False)


if __name__ == "__main__":
    main()
