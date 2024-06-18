import sys
import os


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)

from src3.app import App


def main():

    app = App(window_title="Basic Scene Demo", vertical_sync=False)
    app.run()


if __name__ == "__main__":
    main()
