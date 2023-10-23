# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .amount import Amount
from .currency import Currency


class TotalAmount(core.XsdComplexType):

    def __new__(
        cls,
        total_gross_amount_excluding_third_party_collection: Amount,
        currency: Currency,
        net_total_amount: Amount = None,
        total_deductions_from_amount: Amount = None,
        total_amount_additions: Amount = None,
        total_shipment_costs: Amount = None,
        total_gross_amount_including_third_party_collection: Amount = None,
        tax_line: list = None,
    ) -> dict:
        """
        Totalamount class.

        Args:
            total_gross_amount_excluding_third_party_collection (Amount):
                Net final invoice amount
            currency (Currency): _description_
            net_total_amount (Amount, optional):
                Net final invoice amount
            total_deductions_from_amount (Amount, optional):
                Summary of any deductions
            total_amount_additions (Amount, optional):
                Summary of any additions
            total_shipment_costs (Amount, optional):
                Summary of any shipment costs
            total_gross_amount_including_third_party_collection (Amount, optional):
                Gross invoice amount excluding turnover collected on third-party
                account/for another company
            tax_line (list, optional):
                List of TaxLine
        """
        result = {
            '@total_gross_amount_excluding_third-party_collection':
                total_gross_amount_excluding_third_party_collection,
            '@total_gross_amount_including_third-party_collection':
                total_gross_amount_including_third_party_collection,
            '@net_total_amount': net_total_amount,
            '@total_deductions_from_amount': total_deductions_from_amount,
            '@total_amount_additions': total_amount_additions,
            '@total_shipment_costs': total_shipment_costs,
            '@currency': currency,
            'tax_line': tax_line,
        }
        TotalAmount.validate(result)
        return result
