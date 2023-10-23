# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core


class BankName(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        return (
            value[0:27]
            if len(value) > 27 else
            value
        )
