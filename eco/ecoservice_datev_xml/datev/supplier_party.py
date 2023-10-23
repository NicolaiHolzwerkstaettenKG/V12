# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from .address import Address
from .booking_info_bp import BookingInfoBp
from .country_code import CountryCode
from .invoice_issuer import InvoiceIssuer


class SupplierParty(InvoiceIssuer):
    def __new__(
        cls,
        address: Address,
        account: list,
        booking_info_bp: BookingInfoBp = None,
        ship_to_country: CountryCode = None,
        ship_from_country: CountryCode = None,
    ) -> dict:
        """
        Invoiceissuer class.

        Args:
            address (Address): Address of invoice issuer
            account (Account list): List of bank accounts
            booking_info_bp (BookingInfoBp, optional): Account number of
                business partner from the accounting program
            ship_to_country (str, optional): Shipping country
            ship_from_country (str, optional): Shipping country
        """
        result = super().__new__(
            cls,
            address=address,
            account=account,
            ship_to_country=ship_to_country,
            booking_info_bp=booking_info_bp,
        )
        result.update({
            '@ship_from_country': ship_from_country,
        })
        return result
