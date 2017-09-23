class SifException(Exception):
    pass


class MethodNotFound(SifException):
    pass


class InvalidListener(SifException):
    pass


class ServiceError(SifException):
    pass
