# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .amount import Amount
from .currency import Currency
from .date import Date
from .percentage_ratio import PercentageRatio


class Rebate(core.XsdComplexType):

    def __new__(
        cls,
        rebate_tax: PercentageRatio,
        payment_date: Date = None,
        rebate_percentage: PercentageRatio = None,
        rebate_base_amount: Amount = None,
        rebate_tax_amount: Amount = None,
        rebate_amount: Amount = None,
        currency: Currency = None,
    ) -> dict:
        """
        Rebate Class.

        Args:
        - rebate_tax (PercentageRatio): Tax rate for rebate amount.
        - payment_date (Date, optional):
            Date by which the rebate percentages apply.
        - rebate_percentage (PercentageRatio, optional):
            Percentage rebate deduction.
        - rebate_base_amocunt (Amount, optional):
            Amount from which deduction of rebate is calculated.
        - rebate_tax_amount (Amount, optional): Tax on rebate amount.
        - rebate_amount (Amount, optional): Rebate amount.
        - currency (Currency, optional): Currency code for the above amounts.
        """
        result = {
            '@rebate_tax': rebate_tax,
            '@payment_date': payment_date,
            '@rebate_percentage': rebate_percentage,
            '@rebate_base_amount': rebate_base_amount,
            '@rebate_tax_amount': rebate_tax_amount,
            '@rebate_amount': rebate_amount,
            '@currency': currency,
        }
        Rebate.validate(result)
        return result
