class BaseAppException(Exception):
    """Base exception for our application"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundException(BaseAppException):
    """Raised when a requested resource is not found"""

    def __init__(self, message: str):
        super().__init__(message)


class ValidationException(BaseAppException):
    """Raised when input validation fails"""

    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedException(BaseAppException):
    """Raised when user is not authorized"""

    def __init__(self, message: str):
        super().__init__(message)
