# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import api, fields, models
import re


class ResCompany(models.Model):
    _inherit = 'res.company'

    # region Fields
    chief_executive_officer = fields.Text()
    report_table_position = fields.Boolean(
        string='Show line item number in printed documents',
        default=True,
    )
    report_table_position_continuous = fields.Boolean(
        string='Share continuous line item numbers across all sections',
        default=True,
    )
    standard_document_language = fields.Selection(
        selection='_get_all_languages',
    )
    report_footer_as_image = fields.Boolean(
        default=False,
    )
    report_footer_image = fields.Binary()
    # endregion

    # region Business Methods
    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)

        templates = self.env["text.template.config"].search(
            [("company_id", "=", 1)],
        )
        for company in companies:
            for template in templates:
                self._copy_template_to_company(template, company)
        return companies

    def create_missing_template(self):
        standard_templates = self.env['text.template.config'].search([
            ('company_id', '=', 1),
        ])
        if not standard_templates:
            standard_templates = self._set_template_company_id()
        other_companys = self.env['res.company'].search([('id', '!=', 1)])
        for compnay in other_companys:
            templates = self.env['text.template.config'].search([
                ('company_id', '=', compnay.id),
            ])
            if len(templates) == len(standard_templates):
                continue
            else:
                standard_templates_name = standard_templates.mapped('name')
                for template in standard_templates_name:
                    if template not in templates.mapped('name'):
                        template = standard_templates.search([
                            ('name', '=', template),
                            ('company_id', '=', 1),
                        ], limit=1)
                        self._copy_template_to_company(template, compnay)

    def get_bank_accounts(self):
        if 'account.journal' not in self.env:
            return []

        bank_journal = []
        journals = self.env['account.journal'].search(
            [
                ('company_id', '=', self.id),
                ('type', 'in', ['bank']),
                ('bank_id', '!=', False),
                ('show_bank_data_invoice', '=', True),
            ],
            limit=4,
        )

        if not journals:
            return []

        for journal in journals:
            bank_journal.append(journal)

        return bank_journal

    def _get_all_languages(self):
        return self.env['res.lang'].get_installed()

    def get_footer_as_image(self):
        if self.report_footer_image and self.report_footer_as_image:
            return True
        return False

    def _set_template_company_id(self):
        # Call up all existing templates
        templates = self.env['text.template.config'].search([])
        for template in templates:
            template.company_id = 1
            template.company_xml_id = template.get_external_id()[template.id]
        return templates

    def _copy_template_to_company(self, template, company):
        new_template = self.env["text.template.config"].sudo().create({
            "name": template.name,
            "model": template.model.id,
            "company_id": company.id,
            'company_xml_id': template.get_external_id()[template.id],
        })
        langs = self.env['res.lang'].search([]).mapped('code')
        for lang in langs:
            if lang == self.env.lang:
                continue
            translated_name = template.with_context(lang=lang).name
            if translated_name:
                new_template.with_context(lang=lang).write({
                    'name': translated_name,
                })

    @api.model
    def remove_html_tags(self, html_field):

        text = str(html_field)
        pattern = re.compile(r'<[^>]+>')
        raw_text = pattern.sub("", text).replace("&nbsp;", " ").strip()

        return raw_text
    # endregion
