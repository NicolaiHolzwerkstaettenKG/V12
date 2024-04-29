# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.
{
    # App Information
    'name': 'German Documents (Base)',
    'summary': 'Designed German Documents for Odoo.',
    'category': 'Base',
    'version': '16.0.1.2.5',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://www.ecoservice.de/shop/product/deutsche-dokumente-fur-odoo-47',
    # Odoo Apps Store
    'support': 'deutsche-dokumente@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        # odoo
        'base',
        'sale_management',
        'web',
        # ecoservice
        'ecoservice_partner_salutation',  # eco/finance-interface
         'account',
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'reports/report_base.xml',  # this needs to be before 'data/report_layout'
        'data/paperformat.xml',
        'data/report_layout.xml',
        'reports/report_css.xml',
        'reports/report_snippets.xml',
        'reports/report_snippets_letterhead_reference.xml',
        'views/base_document_layout_views.xml',
        'views/res_company_view.xml',
        'views/res_config_view.xml',
        'views/text_template_config.xml',
        'views/account_journal_views.xml',
    ],
}
