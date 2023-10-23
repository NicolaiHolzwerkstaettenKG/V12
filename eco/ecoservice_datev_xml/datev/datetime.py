# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from datetime import datetime

from . import core


class DateTime(core.XsdSimpleType):
    """
    Specific calendar-based time statement comprising the date and time.
    """

    def __new__(
        cls,
        value: datetime,
    ) -> str:
        if not value:
            return None
        return value.strftime('%Y-%m-%dT%H:%M:%S')
