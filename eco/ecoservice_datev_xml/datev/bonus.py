# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .amount import Amount
from .currency import Currency
from .date import Date
from .percentage_ratio import PercentageRatio


class Bonus(core.XsdComplexType):

    def __new__(
        cls,
        bonus_tax: PercentageRatio,
        payment_date: Date = None,
        bonus_percentage: PercentageRatio = None,
        bonus_base_amount: Amount = None,
        bonus_tax_amount: Amount = None,
        bonus_amount: Amount = None,
        currency: Currency = None,
    ) -> dict:
        result = {
            '@bonus_tax': bonus_tax,
            '@payment_date': payment_date,
            '@bonus_percentage': bonus_percentage,
            '@bonus_base_amount': bonus_base_amount,
            '@bonus_tax_amount': bonus_tax_amount,
            '@bonus_amount': bonus_amount,
            '@currency': currency,
        }
        Bonus.validate(result)
        return result
