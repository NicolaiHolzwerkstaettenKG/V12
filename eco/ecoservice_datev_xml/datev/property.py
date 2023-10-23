# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception
from .description import Description255


class Property(core.XsdComplexType):
    def __new__(
        cls,
        key: str,
        value: Description255,  # noqa: N803
    ) -> dict:
        data = {
            '@key': key,
            '@value': value,
        }
        Property.validate(data)
        return data

    @staticmethod
    def validate(data) -> None:
        Property.validate_key(data)

    @staticmethod
    def validate_key(data):
        value = data.get('@key')
        if len(value) > 15:
            raise exception.DatevXmlLengthError(
                message='Property.key not in range',
                value=value,
                range='1-15',
            )
