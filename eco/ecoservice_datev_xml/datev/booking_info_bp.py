# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception
from .account_number import AccountNumber


class BookingInfoBp(core.XsdComplexType):
    def __new__(
        cls,
        bp_account_no: AccountNumber,
    ) -> dict:
        """
        Bookinginfobp class.

        Args:
            bp_account_no (str): account number of business partner from the
                accounting program
        """
        result = {
            '@bp_account_no': bp_account_no,
        }
        BookingInfoBp.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        BookingInfoBp.bp_account_no(data)

    @staticmethod
    def bp_account_no(data):
        bp_account_no = data.get('@bp_account_no')
        if not bp_account_no:
            raise exception.DatevXmlMissingError(
                field='BookingInfoBp.bp_account_no'
            )
