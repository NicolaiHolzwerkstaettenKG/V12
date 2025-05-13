# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import time

from odoo import api, fields, models


class ExportEcofi(models.TransientModel):
    _name = 'export.ecofi'
    _description = 'Finance Export'

    # region Default

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['journal_ids'] = [
            (6, 0, self.env.company.journal_ids.ids),
        ]
        return defaults

    # endregion

    # region Fields

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda r: r.env.company,
    )
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        relation='export_ecofi_journal_rel',
        column1='export_ecofi_id',
        column2='journal_id',
        required=True,
    )
    date_from = fields.Date(
        default=lambda *a: time.strftime('%Y-%m-01'),
        required=True,
    )
    date_to = fields.Date(
        default=lambda *a: time.strftime('%Y-%m-%d'),
        required=True,
    )

    # endregion

    # region Business Methods

    def start_export(self):
        """
        Start the export through the wizard.
        """
        self.ensure_one()

        model_exists = self.env['ir.module.module'].search(
            [('name', '=', 'ecoservice_financeinterface_datev_xml')],
            limit=1
        )
        if model_exists.state == 'installed':
            vorlauf = self.env['ecofi'].ecofi_buchungen(
                journal_ids=self.journal_ids,
                date_from=self.date_from,
                date_to=self.date_to,
                to_export=self.to_export
            )
        else:
            vorlauf = self.env['ecofi'].ecofi_buchungen(
                journal_ids=self.journal_ids,
                date_from=self.date_from,
                date_to=self.date_to,
            )
        return {
            'name': 'Create Finance Export',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'ecofi',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': vorlauf.id,
        }

    # endregion
