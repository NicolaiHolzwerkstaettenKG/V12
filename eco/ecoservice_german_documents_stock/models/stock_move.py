# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import models


# We need this for the mixin
class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ['stock.move', 'eco_report.mixin']

    def _action_confirm(self, merge=True, merge_into=False):
        results = super(StockMove, self)._action_confirm(merge, merge_into)
        for result in results:
            # only use the sale.order description if no mrp set was used
            # and the products are the same
            # only copy text if the text was changed by hand
            sale = result.sale_line_id
            sale_product = sale.product_id
            move_product = result.product_id
            sale_desc = sale.name
            standard_sale_desc = sale_product.get_product_multiline_description_sale()
            if (
                sale_product.id == move_product.id
                and sale_desc != standard_sale_desc
            ):
                result.description_picking = result.sale_line_id.name
        return results
