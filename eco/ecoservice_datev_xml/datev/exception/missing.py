# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import DatevXmlError


class DatevXmlMissingError(DatevXmlError):
    def __init__(self, field):
        super().__init__(
            message=f'Missing required value for {field}.'
        )
