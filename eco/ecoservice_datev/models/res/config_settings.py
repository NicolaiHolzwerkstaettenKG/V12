# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_code_digits = fields.Integer(
        related='company_id.account_code_digits',
        readonly=False,
    )

    datev_assume_taxfree = fields.Boolean(
        related='company_id.datev_assume_taxfree',
        readonly=False,
    )

    l10n_de_datev_client_number = fields.Char(
        related='company_id.l10n_de_datev_client_number',
        readonly=False,
    )

    l10n_de_datev_consultant_number = fields.Char(
        related='company_id.l10n_de_datev_consultant_number',
        readonly=False,
    )

    tax_consultant_id = fields.Many2one(
        related='company_id.tax_consultant_id',
        readonly=False,
    )
