# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import DatevXmlError


class DatevXmlLengthError(DatevXmlError):
    def __init__(self, message, value, range):  # noqa: A002
        super().__init__(
            message=f'{message}\n"{value}" not in length range {range}'
        )
