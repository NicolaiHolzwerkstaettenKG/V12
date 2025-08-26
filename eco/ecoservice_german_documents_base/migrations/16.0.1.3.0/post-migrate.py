# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Alle bestehenden Templates abrufen
    templates = env['text.template.config'].search([])

    for template in templates:
        template.company_id = 1
        template.company_xml_id = template.get_external_id()[template.id]

    companies = env['res.company'].search([('id', '!=', 1)])
    for company in companies:
        # Alle Templates für die neue Company kopieren
        templates = env['text.template.config'].search([('company_id', '=', 1)])
        for template in templates:
            if template.company_id.id == company.id:
                continue
            new_template = env['text.template.config'].sudo().create({
                'name': template.name,
                'model': template.model.id,
                'default_text': template.default_text,
                'company_id': company.id,
                'company_xml_id': template.get_external_id()[template.id],
            })
            langs = env['res.lang'].search([]).mapped('code')
            for lang in langs:
                if lang == env.lang:
                    continue

                translated_text = template.with_context(lang=lang).default_text
                translated_name = template.with_context(lang=lang).name
                if translated_text:
                    new_template.with_context(lang=lang).write({
                        'default_text': translated_text,
                    })
                if translated_name:
                    new_template.with_context(lang=lang).write({
                        'name': translated_name,
                    })
