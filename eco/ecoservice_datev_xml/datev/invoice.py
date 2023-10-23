# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception
from .accounting_info import AccountingInfo
from .invoice_info import InvoiceInfo
from .invoice_issuer import InvoiceIssuer
from .invoice_participant import InvoiceParticipant
from .payment_conditions import PaymentConditions
from .supplier_party import SupplierParty
from .total_amount import TotalAmount


class Invoice(core.XsdFile):

    def __init__(
        self,
        invoice_info: InvoiceInfo,
        invoice_party: InvoiceIssuer,
        supplier_party: SupplierParty,
        total_amount: TotalAmount,
        invoice_item_list: list,
        delivery_party: InvoiceParticipant = None,
        accounting_info: AccountingInfo = None,
        invoice_recipient: InvoiceParticipant = None,
        delivery_recipient: InvoiceParticipant = None,
        supplier_issuer: InvoiceParticipant = None,
        payment_conditions: PaymentConditions = None,
    ) -> None:
        self.filename = 'Belegverwaltung_online_invoice_v050'
        self.namespaces = {
            '': 'http://xml.datev.de/bedi/tps/invoice/v050',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': (
                'http://xml.datev.de/bedi/tps/invoice/v050 '
                f'{self.filename}.xsd'
            ),
        }
        self.root_attr = {
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': (
                'http://xml.datev.de/bedi/tps/invoice/v050 '
                f'{self.filename}.xsd'
            ),
        }

        data = {
            '@description': 'DATEV Import invoices',
            '@version': '5.0',
            '@generator_info': 'ecoservice GbR',
            '@generating_system': 'Odoo DATEV XML',
            '@xml_data': 'Kopie nur zur Verbuchung berechtigt nicht zum Vorsteuerabzug',
            'invoice_info': invoice_info,
            'invoice_party': invoice_party,
            'invoice_recipient': invoice_recipient,
            'supplier_party': supplier_party,
            'payment_conditions': payment_conditions,
            'invoice_item_list': invoice_item_list,
            'delivery_party': delivery_party,
            'total_amount': total_amount,
            # 'supplier_issuer': supplier_issuer,
            # 'accounting_info': accounting_info,
            # 'delivery_recipient': delivery_recipient,
        }
        self.data = {
            'invoice': data,
        }
        Invoice.validate(data)

    @staticmethod
    def validate(data) -> None:
        Invoice.validate_invoice_info(data)
        Invoice.validate_invoice_party(data)
        Invoice.validate_supplier_party(data)
        Invoice.validate_invoice_item_list(data)

    @staticmethod
    def validate_invoice_item_list(data) -> None:
        value = data.get('invoice_item_list')
        len_value = len(value)
        if len_value < 1 or len_value > 5000:
            raise exception.DatevXmlRangeError(
                message='invoice_item_list out of range.',
                value=len_value,
                range='1-5000',
            )

    @staticmethod
    def validate_invoice_info(data):
        invoice_info = data.get('invoice_info')
        if not invoice_info:
            raise exception.DatevXmlMissingError(
                field='Invoice.invoice_info'
            )

    @staticmethod
    def validate_invoice_party(data):
        invoice_info = data.get('invoice_party')
        if not invoice_info:
            raise exception.DatevXmlMissingError(
                field='Invoice.invoice_party'
            )

    @staticmethod
    def validate_supplier_party(data):
        invoice_info = data.get('supplier_party')
        if not invoice_info:
            raise exception.DatevXmlMissingError(
                field='Invoice.supplier_party'
            )
