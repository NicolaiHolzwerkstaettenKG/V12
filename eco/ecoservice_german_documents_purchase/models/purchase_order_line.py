# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import models


# We need this for the mixin
class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['purchase.order.line', 'eco_report.mixin']

    def report_description(self):
        # 105337: Splitting by \n causes rendering issues!
        return (self.name or '').replace('\n', '<br/>')

    def report_taxes(self):
        return ', '.join(map(
            lambda x: (x.description or x.name),
            self.taxes_id
        ))
