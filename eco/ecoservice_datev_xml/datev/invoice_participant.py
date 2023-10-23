# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception
from .address import Address


class InvoiceParticipant(core.XsdComplexType):
    def __new__(
        cls,
        address: Address,
        account: list,
        vat_id: str = None,
        tax_no: str = None,
    ) -> dict:
        result = {
            'address': address,
            'account': account,
            '@vat_id': vat_id,
            '@tax_no': tax_no,
        }
        InvoiceParticipant.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        InvoiceParticipant.validate_accounts(data)
        InvoiceParticipant.validate_address(data)

    @staticmethod
    def validate_address(data):
        address = data.get('address')
        if not address:
            raise exception.DatevXmlMissingError(
                field='InvoiceParticipant.address'
            )

    @staticmethod
    def validate_accounts(data):
        accounts = data.get('account') or []
        len_accounts = len(accounts)
        if len_accounts > 100:
            raise exception.DatevXmlRangeError(
                message='InvoiceParticipant has too many accounts.',
                value=len_accounts,
                range='0-100',
            )
