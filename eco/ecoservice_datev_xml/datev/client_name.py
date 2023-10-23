# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception


class ClientName(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> int:
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_value(value):
        if not value:
            raise exception.DatevXmlMissingError(field='ClientName.value')

        len_value = len(str(value))
        if len_value < 1 or len_value > 36:
            raise exception.DatevXmlLengthError(
                message='Invalid ClientName length.',
                value=value,
                range='1-36',
            )
