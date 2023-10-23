# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class PercentageRatio(core.XsdSimpleType):
    """
    Input of a percentage ratio.

    The percentage states the ratio of a given value (=100) to the value under
    consideration. Value 0.00 not permitted; no prefixed sign permitted
    """

    def __new__(
        cls,
        value,
    ) -> str:
        value = '{:.2f}'.format(value)
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(r'([1-9]\d{0,1}|0)(\.\d{2})', value):
            raise exception.DatevXmlInvalidError(
                field='PercentageRatio.value',
                value=value,
            )
