# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models, fields


class EcofiExportColumnsConfig(models.Model):
    _name = 'ecofi.export.columns.config'
    _description = 'defines which columns infos will be exported.'

    HEADER = [
        ('Kost1', 'KOST1 - Kostenstelle'),
        ('Kost2', 'KOST2 - Kostenstelle'),
        ('Zusatzinformation - Art 1', 'Zusatzinformation - Art 1'),
        ('ZusatzInhalt1', 'Zusatzinformation- Inhalt 1'),
        ('Auftragsnummer', "Auftragsnummer"),
        ('Leistungsdatum', "Leistungsdatum"),
    ]

    column = fields.Selection(string="Column", selection=HEADER)
    to_export = fields.Boolean(default=True, string="to export")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        ondelete='cascade',
    )
