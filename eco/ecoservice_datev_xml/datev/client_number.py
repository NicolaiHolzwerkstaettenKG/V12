# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class ClientNumber(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> int:
        value = int(value)
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not value:
            raise exception.DatevXmlMissingError(field='ClientNumber.value')

        if value < 0 or value > 999999999:
            # DATEV classic: 5 digits, comfort: 9 digits
            raise exception.DatevXmlRangeError(
                message='Invalid ClientNumber length.',
                value=value,
                range='0-999999999',
            )

        if not re.match(r'([1-9]\d*|0)', str(value)):
            raise exception.DatevXmlInvalidError(
                field='ClientNumber.value',
                value=value,
            )
