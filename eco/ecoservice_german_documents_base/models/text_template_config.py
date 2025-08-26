# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import fields, models


class TextTemplateConfig(models.Model):
    _name = 'text.template.config'
    _description = 'Text Template Config'

    # region Fields
    name = fields.Text(
        string='Description',
        help='Text field, which will be printed in the documents.',
        readonly=True,
        translate=True,
    )
    model = fields.Many2one(
        comodel_name='ir.model',
        readonly=True,
    )
    default_text = fields.Text(
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )
    company_xml_id = fields.Char(
        string="Company XML ID",
    )
    # endregion

    # region Business Methods
    def get_template_text(self, lang, field_xml_list):
        lang = lang or self.env.user.lang or "en_US"
        fields = {}
        for field, xml_id in field_xml_list:
            text_template = self.env['text.template.config'].search([
                ('company_xml_id', '=', xml_id),
                ('company_id', '=', self.env.company.id),
            ], limit=1)
            fields[field] = text_template.with_context(lang=lang).default_text
        return fields
    # endregion
