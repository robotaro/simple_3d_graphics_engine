from core import constants


class Settings:
    """
    Singleton definitions of settings can be used
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)


# Global singleton definition
SETTINGS = Settings()
