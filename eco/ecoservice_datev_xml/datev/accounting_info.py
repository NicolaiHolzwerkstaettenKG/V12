# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from decimal import Decimal

from . import core, exception

from.percentage_ratio import PercentageRatio


class AccountingInfo(core.XsdComplexType):

    def __new__(
        cls,
        booking_text: str,
        cost_category_id: str = None,
        cost_category_id2: str = None,
        cost_amount: Decimal = None,
        account_no: str = None,
        exchange_rate: str = None,
        eu_tax_rate: PercentageRatio = None,
        bu_code: str = None,
        type_of_receivable: str = None,
        accounting_additional_info: list = [],
    ) -> dict:
        """
        Accountinginfo class.

        Args:
            booking_text (str): text which appears in the booking line of the
                booking text.
            cost_category_id (str, optional): Cost centre identification.
            cost_category_id2 (str, optional): Cost unit identification.
            cost_amount (Decimal, optional): Number of cost amount(s).
                Figure given always includes decimal places.
            account_no (str, optional): Impersonal account No. of goods
                inward account or revenue account
            exchange_rate (str, optional): Conversion rate yielded when
                converting foreign currency invoices into euros
            eu_tax_rate (PercentageRatio, optional): EU tax rate for invoices
                from other EU countries
            bu_code (str, optional): BU code (B=Adjustment codecc, U=Tax code)
            type_of_receivable (str, optional): Identification of the order
                number
            accounting_additional_info (list AccountingAdditionalInfo, optional):
                Max. 5 entries.
        """
        result = {
            '@booking_text': booking_text,
            '@cost_category_id': cost_category_id,
            '@cost_category_id2': cost_category_id2,
            '@cost_amount': cost_amount,
            '@account_no': account_no,
            '@exchange_rate': exchange_rate,
            '@eu_tax_rate': eu_tax_rate,
            '@bu_code': bu_code,
            '@type_of_receivable': type_of_receivable,
            'accounting_additional_info': accounting_additional_info,
        }
        AccountingInfo.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        AccountingInfo.validate_booking_text(data)
        AccountingInfo.validate_accounting_additional_info(data)

    @staticmethod
    def validate_booking_text(data):
        booking_text = data.get('@booking_text')

        if not booking_text:
            raise exception.DatevXmlMissingError(field='@booking_text')

        if len(booking_text) > 30:
            raise exception.DatevXmlLengthError(
                message='Booking text cannot exceed 30 characters.',
                value=booking_text,
                range='0-30',
            )

    @staticmethod
    def validate_accounting_additional_info(data):
        additional_info = data.get('accounting_additional_info')
        if additional_info and len(additional_info) > 5:
            raise exception.DatevXmlLengthError(
                message=(
                    'Maximum of 5 accounting additional information '
                    'entries exceeded.'
                ),
                value='[...]',
                range='0-5',
            )
