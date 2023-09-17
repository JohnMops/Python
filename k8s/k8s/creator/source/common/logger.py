import logging
import datetime


class Logger:
    logger = None

    def __init__(self, module):
        self.__module = module
        self.__logger = logging.getLogger(module)
        self.__logger.setLevel(logging.DEBUG)

        # create console handler
        fmt = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)

        self.__logger.addHandler(ch)
        self.__logger.propagate = False

    def __external(self, level, message):
        info = {
            "module": self.__module,
            "timestamp": str(datetime.datetime.now()),
            "level": level,
            "message": message
        }

        # Here comes integration with external logging system

        #print(info)

    def __internal(self, level, message):
        self.__logger.log(level, message, extra = {})

    def debug(self, message):
        self.__external(level = logging.DEBUG, message = message)
        self.__internal(level = logging.DEBUG, message = message)

    def warning(self, message):
        self.__external(level = logging.WARNING, message = message)
        self.__internal(level = logging.WARNING, message = message)

    def info(self, message):
        self.__external(level = logging.INFO, message = message)
        self.__internal(level = logging.INFO, message = message)

    def error(self, message):
        self.__external(level = logging.ERROR, message = message)
        self.__internal(level = logging.ERROR, message = message)