import threading
import time


class Resource:

    def __init__(self):
        self.data_blocks = {}


class ResourceWithThread:
    def __init__(self, path: str):
        self.path = path
        self.is_loaded = False
        self.load_error = None
        self._load_thread = None

    def load(self):
        if self._load_thread and self._load_thread.is_alive():
            return  # The resource is still loading

        self._load_thread = threading.Thread(target=self._load_resource)
        self._load_thread.start()

    def _load_resource(self):
        try:
            # Simulated loading (replace with actual loading logic)
            time.sleep(2)
            self.is_loaded = True
        except Exception as e:
            self.load_error = e
            self.is_loaded = False

    def is_loading(self):
        return self._load_thread and self._load_thread.is_alive()


class TextureResource(Resource):
    def _load_resource(self):
        try:
            # Load texture here...
            time.sleep(2)
            self.is_loaded = True
        except Exception as e:
            self.load_error = e
            self.is_loaded = False
