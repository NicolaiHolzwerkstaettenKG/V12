# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # region Fields
    company_id = fields.Many2one(
        # Field required for Odoo.sh compatibility (#13000).
        comodel_name='res.company',
        default=lambda self: self.env.company.id,
    )
    report_table_position = fields.Boolean(
        related='company_id.report_table_position',
        readonly=False,
    )
    report_table_position_continuous = fields.Boolean(
        related='company_id.report_table_position_continuous',
        readonly=False,
    )
    standard_document_language = fields.Selection(
        related='company_id.standard_document_language',
        readonly=False,
    )
    # endregion

    # region Business Methods
    def change_default_text_template(self):
        self.ensure_one()
        action = self.sudo().env.ref(
            'ecoservice_german_documents_base.text_template_config_action'
        ).read()[0]
        return action
    # endregion
