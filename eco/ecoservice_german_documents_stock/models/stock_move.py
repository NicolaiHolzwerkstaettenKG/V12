# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import models


# We need this for the mixin
class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ['stock.move', 'eco_report.mixin']

    def _action_confirm(self, merge=True, merge_into=False):
        result = super(StockMove, self)._action_confirm(merge, merge_into)
        index = 0
        for sale_line in result.sale_line_id:
            result[index].description_picking = sale_line.name
            index += 1
        return result
