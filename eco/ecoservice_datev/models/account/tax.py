# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_de_datev_code = fields.Char(size=8)
