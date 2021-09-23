"""Exceptions for Efergy API Python client."""


class DataError(Exception):
    """When a data error is encountered."""


class ConnectTimeout(Exception):
    """The request timed out while trying to connect to the remote server."""


class InvalidAuth(Exception):
    """The URL provided was somehow invalid."""
