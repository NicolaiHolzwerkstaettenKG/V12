# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models

from ...datev import (
    AccountNumber,
    Amount,
    BookingInfoBp,
    Currency,
    Date,
    Description40,
    Invoice,
    InvoiceInfo,
    InvoiceIssuer,
    InvoiceParticipant,
    InvoiceType,
    PaymentConditions,
    Property,
    SupplierParty,
    TotalAmount,
)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def datev_booking_info(
        self,
        partner,
        payable: bool,
    ) -> BookingInfoBp:
        account = (
            partner.property_account_payable_id
            if payable else
            partner.property_account_receivable_id
        )
        return BookingInfoBp(
            bp_account_no=AccountNumber(account.code),
        )

    def datev_document_type(self) -> int:
        odoo_types = {
            'entry': None,
            'out_invoice': 2,
            'in_invoice': 1,
            'out_refund': None,
            'in_refund': None,
            'out_receipt': None,
            'in_receipt': None,
        }
        return odoo_types.get(self.move_type, None)

    def datev_invoice_type(self) -> InvoiceType:
        odoo_types = {
            'entry': '',
            'out_invoice': 'Rechnung',
            'in_invoice': 'Rechnung',
            'out_refund': 'Gutschrift/Rechnungskorrektur',
            'in_refund': 'Gutschrift/Rechnungskorrektur',
            'out_receipt': '',
            'in_receipt': '',
        }
        return InvoiceType(odoo_types.get(self.move_type, None))

    def datev_keywords(self):
        return ', '.join(
            filter(None, [
                self.partner_id.name,
                self.partner_id.ref,
            ]))

    def datev_extension_property(self):
        odoo_types = {
            'entry': '',
            'out_invoice': 'Outgoing',
            'in_invoice': 'Incoming',
            'out_refund': 'Outgoing',
            'in_refund': 'Incoming',
            'out_receipt': 'Outgoing',
            'in_receipt': 'Incoming',
        }
        return [
            Property('InvoiceType', odoo_types.get(self.move_type, None)),
            # Property('invoice_date', Date(self.invoice_date)),
            # Property('name', Description255(self.name)),
            # Property('type', Description255(self.move_type)),
        ]

    def datev_invoice_info(self) -> InvoiceInfo:
        order_id = (
            self.invoice_origin
            if self.move_type == 'out_invoice' else
            None
        )

        drawee_no = (
            self.invoice_origin
            if self.move_type in ('in_refund', 'out_refund') else
            None
        )

        return InvoiceInfo(
            invoice_date=Date(self.invoice_date),
            delivery_date=Date(self.invoice_date),
            order_id=order_id,
            invoice_id=Description40(self.name),
            invoice_type=self.datev_invoice_type(),
            drawee_no=drawee_no,
        )

    def datev_invoice_party(self) -> InvoiceIssuer:
        # Leistungsempfänger
        partner = self.company_id.partner_id
        if 'out' in self.move_type:
            partner = self.partner_id

        # in_invoice -> invoice_party -> Payable
        # out_invoice -> invoice_party -> Receivable
        partner_payable = self.move_type in ('in_invoice', 'in_refund')

        return InvoiceIssuer(
            address=partner.datev_address(),
            account=partner.datev_accounts(),
            booking_info_bp=self.datev_booking_info(
                partner=partner,
                payable=partner_payable,
            ),
            ship_to_country=partner.country_id.datev_country_code(),
        )

    def datev_invoice_recipient(self) -> InvoiceParticipant:
        partner = self.company_id.partner_id
        if self.move_type in ('out_invoice', 'out_refund'):
            partner = self.partner_id

        return InvoiceParticipant(
            address=partner.datev_address(),
            account=partner.datev_accounts(),
        )

    def datev_delivery_recipient(self) -> InvoiceParticipant:
        partner = self.partner_shipping_id

        if not partner:
            # No shipping partner provided
            partner = self.company_id.partner_id
            if self.move_type in ('out_invoice', 'out_refund'):
                partner = self.partner_id

        if not partner:
            return None

        return InvoiceParticipant(
            address=partner.datev_address(),
            account=partner.datev_accounts(),
        )

    def datev_payment_conditions(self) -> PaymentConditions:
        text = f'Payment until {self.invoice_date_due}'
        if self.invoice_payment_term_id:
            text = self.invoice_payment_term_id.note
        return PaymentConditions(
            payment_conditions_text=text,
            due_date=Date(self.invoice_date_due),
            currency=Currency(self.currency_id.name),
        )

    def datev_supplier_party(self) -> SupplierParty:
        # Leistungserbringer
        partner = self.partner_id
        if 'out' in self.move_type:
            partner = self.company_id.partner_id

        # in_invoice -> supplier_party -> Payable
        # out_invoice -> supplier_party -> Receivable

        # in_refund -> supplier_party -> Payable
        # out_refund -> supplier_party -> Receivable
        partner_payable = self.move_type in ('in_invoice', 'in_refund')

        return SupplierParty(
            address=partner.datev_address(),
            account=partner.datev_accounts(),
            booking_info_bp=self.datev_booking_info(
                partner=partner,
                payable=partner_payable,
            ),
            ship_from_country=partner.country_id.datev_country_code(),
        )

    def datev_invoice_item_list(self) -> list:
        return [x.datev_invoice_item() for x in self.datev_invoice_lines()]

    def datev_tax_lines(self) -> list:
        return [x.datev_tax_line() for x in self.datev_invoice_lines()]

    def datev_total_amount(self) -> TotalAmount:
        prefix = -1 if 'refund' in self.move_type else 1
        return TotalAmount(
            net_total_amount=Amount(prefix * self.amount_untaxed),
            total_gross_amount_excluding_third_party_collection=Amount(
                prefix * self.amount_total
            ),
            tax_line=self.datev_tax_lines(),
            currency=Currency(self.currency_id.name),
        )

    def datev_invoice(self) -> Invoice:
        invoice_lines = self.datev_invoice_item_list()
        if not invoice_lines:
            return None

        return Invoice(
            invoice_party=self.datev_invoice_party(),
            invoice_info=self.datev_invoice_info(),
            invoice_recipient=self.datev_invoice_recipient(),
            total_amount=self.datev_total_amount(),
            supplier_party=self.datev_supplier_party(),
            delivery_recipient=self.datev_delivery_recipient(),
            accounting_info=None,  # Added on move line level
            payment_conditions=self.datev_payment_conditions(),
            invoice_item_list=invoice_lines,
        )
