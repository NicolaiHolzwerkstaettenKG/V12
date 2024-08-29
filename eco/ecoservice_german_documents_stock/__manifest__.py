# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.
{
    # App Information
    'name': 'German Documents (Stock)',
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
    # 'live_test_url': '',
    'support': 'deutsche-dokumente@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        # odoo
        'stock',
        # ecoervice
        'ecoservice_german_documents_base',  # eco/finance-interface
    ],
    # Data
    'data': [
        'reports/report_stock.xml',
        'reports/report_stock_css.xml',
        'reports/report_stock_document_delivery_note.xml',
        'reports/report_stock_document_picking_operation.xml',
        'reports/report_stock_snippets.xml',
        'reports/report_stock_table.xml',
    ],
}
