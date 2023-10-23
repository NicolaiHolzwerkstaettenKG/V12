# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, exceptions, models

from ...datev import (
    AccountingInfo,
    Amount,
    AmountD3,
    Currency,
    Date,
    Description30,
    Description40,
    InvoiceItemList,
    PercentageRatio,
    PriceLineAmount,
    TaxLine,
)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def datev_accounting_info(self) -> AccountingInfo:
        name = self.name or self.account_id.name
        return AccountingInfo(
            booking_text=Description30(name),
            account_no=int(self.account_id.code),
            bu_code=self.datev_bu_key(),
        )

    def datev_bu_key(self):
        tax = self.tax_ids[0] if len(self.tax_ids) > 0 else None
        if not tax:
            return None
        return (
            int(tax.l10n_de_datev_code)
            if tax.l10n_de_datev_code else
            None
        )

    def datev_price_line_amount(self) -> PriceLineAmount:
        prefix = -1 if 'refund' in self.move_id.move_type else 1
        tax = self.tax_ids[0] if len(self.tax_ids) > 0 else None
        tax_amount = self.price_total - self.price_subtotal
        cause_of_tax_exemption = None
        if not tax or not tax_amount:
            cause_of_tax_exemption = 'Keine Steuer gesetzt'

        return PriceLineAmount(
            tax=PercentageRatio(tax.amount if tax else 0),
            tax_amount=Amount(prefix * tax_amount),
            gross_price_line_amount=Amount(prefix * self.price_total),
            net_price_line_amount=Amount(prefix * self.price_subtotal),
            currency=Currency(self.currency_id.name),
            cause_of_tax_exemption=cause_of_tax_exemption,
        )

    def datev_tax_line(self) -> TaxLine:
        prefix = -1 if 'refund' in self.move_id.move_type else 1
        move = self.move_id

        if not self.tax_ids:
            if not self.company_id.datev_assume_taxfree:
                raise exceptions.UserError(_(
                    f'Account move "{move.name}" (id: {move.id}) owns invoice '
                    f'lines (id: {self.id}) with no set tax. '
                    'DATEV requires you to have taxes set for any invoice line. '
                    'You may export any unset tax field as tax free by enabling '
                    'the behaviour in your settings.'
                ))

            return TaxLine(
                net_price_line_amount=Amount(prefix * self.price_subtotal),
                gross_price_line_amount=Amount(prefix * self.price_total),
                tax_amount=Amount(prefix * (
                    self.price_total - self.price_subtotal
                )),
                tax=PercentageRatio(0),
                currency=Currency(self.currency_id.name),
            )

        if not self.datev_relevant():
            return None

        tax = self.tax_ids[0]
        tax_amount = self.price_total - self.price_subtotal

        return TaxLine(
            net_price_line_amount=Amount(self.price_subtotal),
            gross_price_line_amount=Amount(self.price_total),
            tax_amount=Amount(tax_amount),
            tax=PercentageRatio(tax.amount),
            currency=Currency(self.currency_id.name),
        )

    def datev_invoice_item(self) -> InvoiceItemList:
        name = self.name or self.account_id.name
        product = self.product_id
        tax = self.price_unit * sum(self.tax_ids.mapped('amount')) / 100 + 1
        prefix = -1 if 'refund' in self.move_id.move_type else 1

        return InvoiceItemList(
            description_short=Description40(name),
            quantity=Amount(self.quantity),
            accounting_info=self.datev_accounting_info(),
            delivery_date=Date(self.delivery_date() or self.move_id.invoice_date),
            deliverynote_id=None,  # ToDo
            order_unit=Description40(self.product_uom_id.name),
            price_line_amount=self.datev_price_line_amount(),
            product_id=Description40(product.id),
            net_product_price=AmountD3(prefix * self.price_unit),
            gross_product_price=Amount(prefix * (self.price_unit + tax)),
        )
