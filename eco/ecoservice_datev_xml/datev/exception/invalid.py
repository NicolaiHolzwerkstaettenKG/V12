# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import DatevXmlError


class DatevXmlInvalidError(DatevXmlError):
    def __init__(self, field, value=None):
        super().__init__(
            message=f'Invalid value ({value}) for {field}.'
        )
