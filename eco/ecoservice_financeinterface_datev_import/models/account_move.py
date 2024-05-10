# Part of Odoo. Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE at the root directory of this module for full copyright and licensing details.

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    datev_automatic_account = fields.Boolean()


class AccountMove(models.Model):
    _inherit = 'account.move'

    import_datev = fields.Many2one(comodel_name='import.datev', string='DATEV Import', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # region Fields

    datev_posting_key = fields.Selection(
        selection=[
            ('40', '40'),
            ('SD', 'Steuer Direkt'),
        ],
        string='Datev BU',
    )
