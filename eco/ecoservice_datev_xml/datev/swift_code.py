# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class SwiftCode(core.XsdSimpleType):
    def __new__(
        cls,
        value,
    ) -> str:
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(
            r'([A-Z]{4}[A-Z]{2}([A-Z0-9]){2}([A-Z0-9]){0,3})',
            value or '',
        ):
            raise exception.DatevXmlInvalidError(
                field='SwiftCode.value',
                value=value,
            )
