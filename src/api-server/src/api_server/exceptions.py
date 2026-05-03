"""Exceptions type system the application support."""


class BaseException(Exception):
    """Base class for all app related exceptions."""


class NotAuthenticated(BaseException):
    """Invalid or missing API Key."""


class BatchNotFound(BaseException):
    """Batch not registered in the system."""
