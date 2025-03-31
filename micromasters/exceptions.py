"""
Custom exceptions for the MicroMasters app
"""

from django.core.exceptions import ImproperlyConfigured


class PossiblyImproperlyConfigured(ImproperlyConfigured):
    """
    Custom exception to be raised when the improper configuration is not certain
    """
