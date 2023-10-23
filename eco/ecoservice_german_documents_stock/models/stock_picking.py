# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'eco_report.mixin']

    # region Compute Methods
    def _compute_date(self):
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
