# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

import re
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_shipping_addresses_by_order(self, move):
        """Return dict mapping sale order ID -> shipping address, if multiple exist"""
        if not move.invoice_line_ids:
            return {}

        sales = move.invoice_line_ids.mapped('sale_line_ids.order_id')
        shipping_addresses = sales.mapped('partner_shipping_id')

        if len(set(shipping_addresses)) <= 1:
            return {}

        return {sale.id: sale.partner_shipping_id for sale in sales}

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Create invoices and insert shipping notes directly before related invoice lines by batch invoices."""
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)

        for move in moves:
            sale_to_shipping = self._get_shipping_addresses_by_order(move)
            if not sale_to_shipping:
                continue

            handled_sales = set()
            for line in move.invoice_line_ids.filtered(
                lambda l: l.display_type == 'product'
            ).sorted(key=lambda l: l.sequence):
                sale_orders = line.sale_line_ids.mapped('order_id')
                if not sale_orders:
                    continue

                sale_order = sale_orders[0]
                sale_id = sale_order.id

                if sale_id in handled_sales:
                    continue  # Note for this order has already been created

                shipping_partner = sale_to_shipping.get(sale_id)
                if not shipping_partner:
                    continue

                handled_sales.add(sale_id)

                contact_address = re.sub(r'\n{2,}', '\n', shipping_partner.contact_address_complete.strip())
                note_text = f"{sale_order.name}\n{shipping_partner.name}\n{contact_address}"

                # Insert new note line directly in front of the product line
                move.env['account.move.line'].create({
                    'move_id': move.id,
                    'display_type': 'line_note',
                    'name': note_text,
                    'sequence': line.sequence - 0.01,  # comes directly before the corresponding line
                })

            move.print_shipping_address = False

        return moves
    # endregion
