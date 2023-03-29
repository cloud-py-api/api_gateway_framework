"""
Exceptions for the Nextcloud API.
"""
from typing import Union


class NextcloudException(Exception):
    status_code = Union[int, None]
    reason = None

    def __init__(self, status_code: int = None, reason: str = None):
        super(BaseException, self).__init__()
        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return f"[{self.status_code}] {self.reason}" if self.status_code else self.reason


class NextcloudRequestTimeout(NextcloudException):
    status_code = 408
    reason = "Request timeout."

    def __init__(self):
        super(NextcloudException, self).__init__()


class NextcloudBadRequest(NextcloudException):
    status_code = 400
    reason = "Bad request."

    def __init__(self):
        super(NextcloudException, self).__init__()


class NextcloudUnauthorized(NextcloudException):
    status_code = 401
    reason = "Invalid credentials."

    def __init__(self):
        super(NextcloudException, self).__init__()


class NextcloudForbidden(NextcloudException):
    status_code = 403
    reason = "Forbidden action due to permissions."

    def __init__(self):
        super(NextcloudException, self).__init__()


class NextcloudNotFound(NextcloudException):
    status_code = 404
    reason = "Not found."

    def __init__(self):
        super(NextcloudException, self).__init__()


class NextcloudMethodNotAllowed(NextcloudException):
    status_code = 405
    reason = "Method not allowed."

    def __init__(self):
        super(NextcloudException, self).__init__()
