# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class BankCode(core.XsdSimpleType):
    def __new__(
        cls,
        value,
    ) -> str:
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(r'([1-9]|[0-9]{2,10})', value):
            raise exception.DatevXmlInvalidError(
                field='BankCode.value',
                value=value,
            )
