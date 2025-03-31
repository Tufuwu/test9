"""
Validate course prices
"""
from django.core.management import BaseCommand, CommandError

from ecommerce.api import validate_prices


class Command(BaseCommand):
    """
    Validate prices and financial aid
    """
    help = "Validate course prices and financial aid discounts"

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        errors = validate_prices()
        if errors:
            raise CommandError(errors)
