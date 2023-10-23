# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class IBAN(core.XsdSimpleType):
    def __new__(
        cls,
        value,
    ) -> str:
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(r'([A-Z]{2}\d\d([A-Za-z0-9]){11,30})', value):
            raise exception.DatevXmlInvalidError(
                field='IBAN.value',
                value=value,
            )
