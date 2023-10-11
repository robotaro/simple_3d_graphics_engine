import logging


class SingletonLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize_logger()
            logging.Logger.manager.loggerDict['singleton_logger'] = cls._instance
        return cls._instance

    def _initialize_logger(self):
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)

        # Create and configure your desired logging handler and formatter here
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)


def get_project_logger(project_logger_name="project_logger"):
    logger = logging.getLogger(project_logger_name)
    logger.setLevel(logging.DEBUG)  # Set the desired logging level for your project

    # Check if the logger already has any handlers
    if not logger.handlers:
        # Create and configure your desired logging handler and formatter here
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger