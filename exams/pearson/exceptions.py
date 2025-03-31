"""
Exceptions for exams
"""


class InvalidTsvRowException(Exception):
    """
    A row for a tsv is invalid
    """


class InvalidProfileDataException(InvalidTsvRowException):
    """
    Profile contains invalid data to sync
    """


class UnparsableRowException(InvalidTsvRowException):
    """
    Row from a TSV was unparsable
    """


class RetryableSFTPException(Exception):
    """
    A retryable exception during SFTP upload

    Usually this is a transient connection or SSH error.
    """
