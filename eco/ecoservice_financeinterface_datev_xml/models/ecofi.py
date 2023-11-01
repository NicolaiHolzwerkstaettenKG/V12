# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class Ecofi(models.Model):
    _inherit = 'ecofi'

    xml_export_id = fields.Many2one(
        string='XML Export',
        comodel_name='datev.export',
    )
    xml_export_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        related='xml_export_id.archive_id',
    )
    xml_export_file = fields.Binary(
        string='Attachment',
        related='xml_export_attachment_id.datas',
    )

    def set_beleglink(self, move, line, datevdict):
        company = self.company_id or self.env.company
        datevdict['Beleglink'] = '{link_type} ""{link}""'.format(
            link_type=company.export_document_link_type.upper(),
            link=move.get_uuid4(),
        )
        return super(Ecofi, self).set_beleglink(move, line, datevdict)

    def export_csv_xml(self, journal_ids):
        if not self.xml_export_id:
            self.xml_export_id = self.xml_export_id.sudo().create({
                'type': 'xml_csv_extension',
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
        else:
            self.xml_export_id.reset()
            self.xml_export_id.date_from = self.date_from
            self.xml_export_id.date_to = self.date_to

        self.xml_export_id.export()

    def unlink(self):
        xml_export = self.xml_export_id
        res = super(Ecofi, self).unlink()
        xml_export.reset()
        xml_export.unlink()
        return res

    def ecofi_buchungen(self, journal_ids, date_from, date_to):
        vid = super().ecofi_buchungen(journal_ids, date_from, date_to)
        vid.export_csv_xml(journal_ids)
        return vid
