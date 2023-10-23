# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.
{
    # App Information
    'name': 'German Documents',
    'summary': 'Designed German Documents for Odoo.',
    'category': 'Base',
    'version': '16.0.1.0.1',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://www.ecoservice.de/shop/product/deutsche-dokumente-fur-odoo-47',
    # Odoo Apps Store
    'price': 650.00,
    'currency': 'EUR',
    # 'live_test_url': 'https://eco-german-documents-13-0.test.ecoservice.de/',
    'support': 'deutsche-dokumente@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        # ecoservice
        'ecoservice_german_documents_base',  # eco/finance-interface
        'ecoservice_german_documents_invoice',  # eco/finance-interface
        'ecoservice_german_documents_purchase',  # eco/finance-interface
        'ecoservice_german_documents_sale',  # eco/finance-interface
        'ecoservice_german_documents_stock',  # eco/finance-interface
    ],
}
