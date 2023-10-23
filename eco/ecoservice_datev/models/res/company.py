# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_code_digits = fields.Integer(
        string='Number of digits in an account code',
    )
    datev_assume_taxfree = fields.Boolean(
        string='Missing tax as tax free',
        default=True,
    )
    l10n_de_datev_consultant_number = fields.Char(
        string='Consultant No.',
        size=7,
    )
    l10n_de_datev_client_number = fields.Char(
        string='Client No.',
        size=9,
    )
