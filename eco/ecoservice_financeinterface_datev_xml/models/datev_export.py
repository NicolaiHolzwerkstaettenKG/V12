# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, exceptions, models


class DatevExport(models.Model):
    _inherit = 'datev.export'

    def moves(self):
        if self.type != 'xml_csv_extension':
            return super(DatevExport, self).moves()

        ecofi = self.env['ecofi'].sudo()
        ecofi = ecofi.search([('xml_export_id', '=', self.id)], limit=1)
        if not ecofi:
            raise exceptions.UserError(_('Related CSV export not found.'))
        return ecofi.account_moves
