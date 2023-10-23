# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class AccountNumber(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> int:
        cls.validate_value(value)
        return int(value)

    @staticmethod
    def validate_value(value):
        if not value:
            raise exception.DatevXmlMissingError(field='AccountNumber.value')

        len_value = len(str(value))
        if len_value < 5 or len_value > 9:
            raise exception.DatevXmlLengthError(
                message='Invalid account number length.',
                value=value,
                range='5-9'
            )

        if not re.match(r'([1-9]\d*|0)', value):
            raise exception.DatevXmlInvalidError(
                field='AccountNumber.value',
                value=value,
            )
