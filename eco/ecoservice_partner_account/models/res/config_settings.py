# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # region Fields

    partner_account_generate_automatically = fields.Boolean(
        related='company_id.partner_account_generate_automatically',
        readonly=False,
    )
    shared_partner_accounts = fields.Boolean(
        related='company_id.shared_partner_accounts',
        readonly=False,
    )
    partner_ref_source = fields.Selection(
        related='company_id.partner_ref_source',
        readonly=False,
        required=True,
    )
    module_ecoservice_partner_account_confirm_sale = fields.Boolean(
        string='Create Debitor Account on Sale Order Confirm'
    )
    module_ecoservice_partner_account_confirm_purchase = fields.Boolean(
        string='Create Creditor Account on Puchase Order confirm'
    )

    # endregion
