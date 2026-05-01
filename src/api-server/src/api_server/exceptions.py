"""Exceptions type system the application support."""


class BaseException(Exception):
    """Base class for all app related exceptions."""


class NotAuthenticated(BaseException):
    """Invalid or missing API Key."""
