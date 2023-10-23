# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .amount import Amount
from .currency import Currency
from .percentage_ratio import PercentageRatio


class TaxLine(core.XsdComplexType):

    def __new__(
        cls,
        tax: PercentageRatio,
        net_price_line_amount: Amount = None,
        gross_price_line_amount: Amount = None,
        tax_amount: Amount = None,
        currency: Currency = None,
    ) -> dict:
        result = {
            '@tax': tax,
            '@net_price_line_amount': net_price_line_amount,
            '@gross_price_line_amount': gross_price_line_amount,
            '@tax_amount': tax_amount,
            '@currency': currency,
        }
        TaxLine.validate(result)
        return result
