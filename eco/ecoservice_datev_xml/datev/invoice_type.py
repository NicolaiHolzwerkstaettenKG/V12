# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception


class InvoiceType(core.XsdSimpleType):
    """
    InvoiceType Class.

    Valid Values:
    - Abschlagsrechnung
    - Bargutschrift
    - Barrechnung
    - Barrechnungskorrektur
    - Gutschrift § 14 UStG
    - Gutschrift/Rechnungskorrektur
    - Rechnung
    - Rechnungskorrektur
    - Schlussrechnung
    """

    def __new__(
        cls,
        value: str,
    ) -> str:
        cls.validate_value(value)
        return value

    @staticmethod
    def valid_values():
        return [
            'Abschlagsrechnung', 'Bargutschrift', 'Barrechnung',
            'Barrechnungskorrektur', 'Gutschrift § 14 UStG',
            'Gutschrift/Rechnungskorrektur', 'Rechnung', 'Rechnungskorrektur',
            'Schlussrechnung'
        ]

    @staticmethod
    def validate_value(value):
        if value not in InvoiceType.valid_values():
            raise exception.DatevXmlInvalidError(
                field='InvoiceType.value',
                value=value,
            )
