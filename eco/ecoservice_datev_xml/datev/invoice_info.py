# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .date import Date
from .invoice_type import InvoiceType


class InvoiceInfo(core.XsdComplexType):
    def __new__(
        cls,
        invoice_date: Date,
        invoice_type: InvoiceType,
        delivery_date: Date,
        invoice_id: str,
        drawee_no: str = None,
        order_id: str = None,
    ) -> dict:
        """
        Invoiceinfo class.

        Args:
            invoice_date (date): Date of invoice
            invoice_type (InvoiceType): Value of the invoice or credit note
            delivery_date (date): Date of delivery or service
            invoice_id (str): Invoice number
            drawee_no (str, optional): Credit note related invoice number
            order_id (str, optional): Order reference
        """
        result = {
            '@invoice_date': invoice_date,
            '@invoice_type': invoice_type,
            '@delivery_date': delivery_date,
            '@invoice_id': invoice_id,
            '@drawee_no': drawee_no,
            '@order_id': order_id,
        }
        return result
