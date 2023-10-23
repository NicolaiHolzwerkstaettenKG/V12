# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, exceptions, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    datev_export = fields.Many2one(related='move_id.datev_export')

    def write(self, vals):
        self.datev_legal_revision_security(vals)
        return super().write(vals)

    def datev_legal_revision_security(self, vals={}):
        for rec in self:
            if not rec.datev_export:
                continue

            vkeys = set(vals.keys())
            safe_vkeys = set(
                self.datev_excluded_revision_fields()
                + self.computed_fields()
            )

            if vals and vkeys.issubset(safe_vkeys):
                continue

            raise exceptions.UserError(_(
                'The record was exported to the accountant and/or tax office. '
                'Due to legal revision restrictions the move line can not '
                'be modified.'
            ))

    def computed_fields(self) -> list:
        result = []
        for fname, fdata in self.fields_get().items():
            if fdata.get('depends'):
                result.append(fname)
        return result

    def datev_excluded_revision_fields(self) -> list:
        return [
            'full_reconcile_id',
            'followup_line_id',
            'last_followup_date',
            'expected_pay_date',
            'blocked',
        ]

    def delivery_date(self):
        sales = self.sale_line_ids.mapped('order_id').filtered(
            lambda x: x.commitment_date
        )
        return sales[0].commitment_date if sales else None

    def total_tax_amount(self):
        """Return the total tax amount to be paid for this line."""
        return self.price_total - self.price_subtotal

    def datev_relevant(self):
        """Return if the move line must be reported to datev.

        Monetary values of value 0 aswell as taxes resulting in 0 can often
        be skipped depending on the countries tax laws.
        """
        return bool(self.total_tax_amount())
