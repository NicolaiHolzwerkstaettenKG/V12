# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .bank_code import BankCode
from .bank_name import BankName
from .country_code import CountryCode
from .iban import IBAN
from .swift_code import SwiftCode


class Account(core.XsdComplexType):
    def __new__(
        cls,
        bank_name: BankName,
        bank_account: str = None,
        bank_code: BankCode = None,
        bank_country: CountryCode = None,
        iban: IBAN = None,
        swiftcode: SwiftCode = None,
    ) -> dict:
        """
        Account Class.

        Args:
            bank_name (str): Name of bank
            bank_account (str, optional): Bank account number
            bank_code (str, optional): Bank sort code
            bank_country (str, optional): Bank country identification
            iban (str, optional): Bank IBAN
            swiftcode (str, optional): Bank Swift code
        """
        return {
            '@bank_name': bank_name,
            '@bank_account': bank_account,
            '@bank_code': bank_code,
            '@bank_country': bank_country,
            '@iban': iban,
            '@swiftcode': swiftcode,
        }
