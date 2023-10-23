# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import models


# We need this for the mixin
class AccountInvoiceLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'eco_report.mixin']

    def is_down_payment(self):
        """Return if the current invoice line is a has down invoice line."""
        downpayment_line = self.mapped('sale_line_ids').filtered(
            lambda line: line.is_downpayment
        )
        return not self.quantity < 0 and downpayment_line
