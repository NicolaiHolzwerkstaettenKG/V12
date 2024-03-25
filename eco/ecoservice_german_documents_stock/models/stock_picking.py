# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'eco_report.mixin']

    signing_date = fields.Date(string='Signing Date', store=True, readonly=True, copy=False)
    signer_name = fields.Char(string='Signer Name', store=True, readonly=True, copy=False)

    # region Compute Methods
    def _compute_dates(self):
        for rec in self:
            date = (
                rec.date_done
                if rec.date_done and rec.state == 'done' else
                rec.scheduled_date
            )
            rec.report_compute_date = fields.Date.context_today(
                rec,
                fields.Datetime.from_string(date or ''),
            )
    # endregion

    # region Business Methods
    def do_print_picking(self):
        super(StockPicking, self).do_print_picking()
        return self.env.ref('stock.action_report_delivery').report_action(self)

    def _get_prefixes(self):
        if self._context.get('report_xml_id') in self._get_packing_reports():
            return [_('Packing-Slip')]
        return [_('Delivery-Note')]

    @api.model
    def _get_packing_reports(self):
        return [
            'stock.report_picking',
            'ecoservice_german_documents_stock'
            '.report_stock_picking_operation_template',
            'ecoservice_german_documents_stock'
            '.report_stock_picking_operation_template_without_logo',
        ]
    # endregion

    def _attach_sign(self):
        self.ensure_one()

        current_date = fields.Date.today()
        signer_name = self.partner_id.name if self.partner_id else None

        if signer_name:
            self.write({'signing_date': current_date, 'signer_name': signer_name})
        else:
            self.write({'signing_date': current_date})

        return super()._attach_sign()

    def get_signed_by(self):
        related_sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
        return related_sale_order.signed_by

    def get_signature(self):
        related_sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
        return related_sale_order.signature
