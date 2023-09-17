
import kopf

class Exception(kopf.PermanentError):
    def __init__(self, logger, message):
        super().__init__(message)

        logger.error(message)