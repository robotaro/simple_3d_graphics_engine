from core import constants


class Settings:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._gui_counter = 0

    def next_gui_id(self):
        self._gui_counter += 1
        return self._gui_counter


# Global singleton definition
SETTINGS = Settings()
