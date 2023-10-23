# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .amount import Amount
from .currency import Currency
from .description import Description40
from .percentage_ratio import PercentageRatio


class PriceLineAmount(core.XsdComplexType):

    def __new__(
        cls,
        tax: PercentageRatio,
        net_price_line_amount: Amount = None,
        gross_price_line_amount: Amount = None,
        tax_amount: Amount = None,
        currency: Currency = None,
        cause_of_tax_exemption: Description40 = None,
    ) -> dict:
        """
        Pricelineamount class.

        Args:
            - tax (PercentageRatio): Tax rate on line amount
            - net_price_line_amount (Amount, optional):
                Net line amount to two decimal places
            - gross_price_line_amount (Amount, optional):
                Gross line amount to two decimal places
            - tax_amount (Amount, optional):
                Tax on line amount to two decimal places
            - currency (Currency, optional): Currency
            - cause_of_tax_exemption (Description40, optional):
                Exact reason why the product is tax-exempt
        """
        result = {
            '@tax': tax,
            '@net_price_line_amount': net_price_line_amount,
            '@gross_price_line_amount': gross_price_line_amount,
            '@tax_amount': tax_amount,
            '@currency': currency,
            '@cause_of_tax_exemption': cause_of_tax_exemption,
        }
        PriceLineAmount.validate(result)
        return result
