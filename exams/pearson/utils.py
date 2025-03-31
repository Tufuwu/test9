"""Utilities for Pearson-specific code"""
from datetime import datetime
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import pytz

from exams.pearson.exceptions import UnparsableRowException
from exams.pearson.constants import PEARSON_DATETIME_FORMATS

from mail import api as mail_api

ZIP_FILE_RE = re.compile(r'^.+\.zip$')


def is_zip_file(filename):
    """
    Checks if a filename looks like a zip file

    Args:
        filename (str): filename to check
    Returns:
        bool: True if the file is a zip file
    """
    return bool(ZIP_FILE_RE.match(filename))


def parse_or_default(parser, default):
    """
    Generate a function that safely parses a value or returns the default

    Args:
        parser (callable): callable to parse the value
        default (Any): default value if parser fails

    Returns:
        callable: function that returns the parser's return value if it succeeds, otherwise it returns the default
    """
    def inner(value):
        """Inner function that performs the safe parsing"""
        try:
            return parser(value)
        except (ValueError, TypeError, UnparsableRowException):
            return default
    return inner


parse_int_or_none = parse_or_default(int, None)


parse_float_or_none = parse_or_default(float, None)


def parse_datetime(dt_string):
    """
    Attempts to parse a datetime string with any one of the datetime formats that we
    expect from Pearson

    Args:
        dt_string (str): datetime string to be parsed

    Returns:
        datetime.datetime: parsed datetime

    Raises:
        UnparsableRowException:
            Thrown if the datetime string cannot be parsed with any of the accepted formats
    """
    for dt_format in PEARSON_DATETIME_FORMATS:
        try:
            return datetime.strptime(dt_string, dt_format).replace(tzinfo=pytz.UTC)
        except ValueError:
            pass
    raise UnparsableRowException('Unparsable datetime: {}'.format(dt_string))


def parse_bool(value):
    """
    Parses boolean values as formatted by Pearson

    Args:
        value (str): boolean string representation

    Returns:
        bool: parsed boolean value

    Raises:
        UnparsableRowException:
            Thrown if the value cannot be parsed as a boolean
    """
    value = value.lower()
    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        raise UnparsableRowException('Unexpected boolean value: {}'.format(value))


def email_processing_failures(filename, zipfile, messages):
    """
    Email summary of failures to mm admin

    Args:
        filename(str): Path of file on local machine.
        zipfile(str): Filename of the zip file
        messages(list): List of error messages compiled in processing
            Exam Authorization Confirmation files (EAC) file.
    """
    if getattr(settings, 'ADMIN_EMAIL', None) is None:
        raise ImproperlyConfigured('Setting ADMIN_EMAIL is not set')

    error_messages = '\n'.join('- {}'.format(message) for message in messages)
    subject = "Summary of failures of Pearson file='{file}'".format(file=filename)
    body = (
        "Hi,\n"
        "The following errors were found in the file {filename} in {zipfile}:\n\n"
        "{messages}"
    ).format(
        messages=error_messages,
        filename=filename,
        zipfile=zipfile
    )

    mail_api.MailgunClient().send_individual_email(
        subject,
        body,
        settings.ADMIN_EMAIL
    )
