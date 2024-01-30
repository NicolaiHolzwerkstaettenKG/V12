# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    show_bank_data_invoice = fields.Boolean(string='Display bank details')
