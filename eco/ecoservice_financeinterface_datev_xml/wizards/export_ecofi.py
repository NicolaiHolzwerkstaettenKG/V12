# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.


from odoo import fields, models


class ExportEcofi(models.TransientModel):
    _inherit = 'export.ecofi'

    # region Fields
    to_export = fields.Selection(
        selection=[
            ("csv_export", "CSV-Export"),
            ("belege_export", "Belege Export"),
            ("csv_and_beleg_export", "CSV+Beleg Export"),
        ],
        default="csv_and_beleg_export",
        required=True,
    )

    # endregion
