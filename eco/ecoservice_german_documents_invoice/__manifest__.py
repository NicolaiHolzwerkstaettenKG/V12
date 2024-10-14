# Extension of Odoo. Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE at the root directory of this module for full copyright and licensing details.
{
    # App Information
    'name': 'German Documents (Invoice)',
    'summary': 'Designed German Documents for Odoo.',
    'category': 'Base',
    'version': '16.0.1.1.10',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://www.ecoservice.de/shop/product/deutsche-dokumente-fur-odoo-47',
    # Odoo Apps Store
    'live_test_url': 'https://eco-german-documents-14-0.test.ecoservice.de/',
    'support': 'deutsche-dokumente@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        # odoo
        'account',
        # ecoservice
        'ecoservice_german_documents_base',  # eco/finance-interface
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'data/text_template.xml',
        'reports/report_invoice.xml',
        'reports/report_invoice_css.xml',
        'reports/report_invoice_document.xml',
        'reports/report_invoice_snippets.xml',
        'reports/report_invoice_table.xml',
        'views/account_view.xml',
        'views/res_config_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
