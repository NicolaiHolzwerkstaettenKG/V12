# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class Ecofi(models.Model):
    _inherit = 'ecofi'

    auto_datev_export = fields.Many2one(
        comodel_name='auto.datev.export.config',
        string='Auto Datev Export'
    )
