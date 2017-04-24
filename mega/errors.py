class ValidationError(Exception):
    """
    Error in validation stage
    """
    pass


class RequestError(Exception):
    """
    Error in API request
    """
    def __init__(self, message, code=None):
        self.code = code
        super(RequestError, self).__init__(message)

