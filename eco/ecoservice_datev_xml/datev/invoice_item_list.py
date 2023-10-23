# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from decimal import Decimal

from . import core, exception
from .accounting_info import AccountingInfo
from .amount import Amount, AmountD3
from .date import Date
from .description import Description40
from .price_line_amount import PriceLineAmount


class InvoiceItemList(core.XsdComplexType):

    def __new__(
        cls,
        description_short: Description40,
        quantity: Decimal,
        price_line_amount: PriceLineAmount,
        accounting_info: AccountingInfo = None,
        deliverynote_id: Description40 = None,
        delivery_date: Date = None,
        product_id: Description40 = None,
        order_unit: Description40 = None,
        net_product_price: AmountD3 = None,
        gross_product_price: Amount = None,
    ) -> dict:
        """
        Invoiceitemlist class.

        Args:
            - description_short (Description40): Prodct description
            - quantity (Decimal): Quantity
            - price_line_amount (PriceLineAmount):
                Comprise the individual product price times the quantity
            - accounting_info (AccountingInfo, optional):
                Booking information at individual line level, such as the
                impersonal account number or information on cost centres
            - deliverynote_id (Description40, optional): Delivery note number
            - delivery_date (Date, optional): Date of delivery
            - product_id (Description40, optional): Product number
            - order_unit (Description40, optional): Unit of Measurement
            - net_product_price (AmountD3, optional):
                Individual net product price
            - gross_product_price (Amount, optional):
                Individual gross product price
        """
        result = {
            'price_line_amount': price_line_amount,
            'accounting_info': accounting_info,
            '@description_short': description_short,
            '@quantity': quantity,
            'price_line_amount': price_line_amount,
            '@deliverynote_id': deliverynote_id,
            '@delivery_date': delivery_date,
            '@product_id': product_id,
            '@order_unit': order_unit,
            '@net_product_price': net_product_price,
            '@gross_product_price': gross_product_price,
        }
        InvoiceItemList.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        InvoiceItemList.validate_delivery_date(data)
        InvoiceItemList.validate_price_line_amount(data)

    @staticmethod
    def validate_delivery_date(data):
        value = data.get('@delivery_date')
        if not value:
            raise exception.DatevXmlInvalidError(
                field='InvoiceItemList.delivery_date',
                value=value,
            )

    @staticmethod
    def validate_price_line_amount(data) -> None:
        value = data.get('price_line_amount')
        if not value:
            raise exception.DatevXmlMissingError(
                field='InvoiceItemList.price_line_amount',
            )
