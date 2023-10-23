# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from datetime import date

from . import core


class Date(core.XsdSimpleType):
    """
    Specific calendar-based time statement comprising the year, month and day.
    """

    def __new__(
        cls,
        value: date,
    ) -> str:
        if not value:
            return None
        return value.strftime('%Y-%m-%d')
