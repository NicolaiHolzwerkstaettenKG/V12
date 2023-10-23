# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.
{
    # App Information
    'name': 'German Documents (Purchase)',
    'summary': 'Designed German Documents for Odoo.',
    'category': 'Base',
    'version': '16.0.1.0.2',
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
        'purchase',
        # ecoservice
        'ecoservice_german_documents_base',  # eco/finance-interface
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'data/text_template.xml',
        'reports/report_purchase.xml',
        'reports/report_purchase_css.xml',
        'reports/report_purchase_document.xml',
        'reports/report_purchase_snippets.xml',
        'reports/report_purchase_table.xml',
        'views/purchase_view.xml',
    ],
}
