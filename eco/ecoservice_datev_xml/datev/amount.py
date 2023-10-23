# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core, exception


class Amount(core.XsdSimpleType):
    """
    Used for amount fields not represented otherwise.

    Amount fields for all amount entry options (e.g., invoice amount,
    tax amount, etc.)
    - Amount of 0.00 not permitted;
    - Only minus sign before amount allowed.
    """

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        value = '{:.2f}'.format(value)
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(r'[\+\-]?([1-9]\d{0,9}|0)(\.\d{2})', value):
            raise exception.DatevXmlInvalidError(
                field='Amount.value',
                value=value,
            )


class AmountD3(core.XsdSimpleType):
    """
    Used for amounts with 3 decimal places.

    Amount fields for all amount entry options (e.g., invoice amount,
    tax amount, etc.)
    - Amount of 0.000 not permitted;
    - Only minus sign before amount allowed.
    """

    def __new__(
        cls,
        value,
    ) -> str:
        value = '{:.3f}'.format(value)
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not re.match(r'[\+\-]?([1-9]\d{0,9}|0)(\.\d{3})', value):
            raise exception.DatevXmlInvalidError(
                field='AmountD3.value',
                value=value,
            )
