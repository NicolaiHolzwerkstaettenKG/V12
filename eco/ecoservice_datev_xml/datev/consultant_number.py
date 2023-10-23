# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class ConsultantNumber(core.XsdSimpleType):

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
            raise exception.DatevXmlMissingError(field='ConsultantNumber.value')

        if value < 1000 or value > 9999999:
            raise exception.DatevXmlRangeError(
                message='Invalid ConsultantNumber length.',
                value=value,
                range='1000-9999999'
            )

        if not re.match(r'([1-9]\d*|0)', str(value)):
            raise exception.DatevXmlInvalidError(
                field='ConsultantNumber.value',
                value=value,
            )
