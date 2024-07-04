# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'German Documents (reminder)',
    'summary': 'Designed German Documents for Odoo.',
    'version': '16.0.1.1.1',
    'category': 'Base',
    'license': 'OPL-1',
    # Author
    'author': 'ecoservice GbR',
    'maintainer': 'ecoservice GbR',
    'website': 'https://www.ecoservice.de',
    'support': 'info@ecoservice.de',
    # Odoo Apps Store
    'price': 0.00,
    'currency': 'EUR',
    'images': [],
    # 'live_test_url': 'https://...',
    # App Installation
    'application': False,
    'installable': True,
    'auto_install': False,
    # Dependencies
    'depends': [
        'account_followup',
        'ecoservice_german_documents_base',
        'ecoservice_german_documents_invoice',
    ],
    'external_dependencies': {},
    # Data
    'data': [
        'reports/report_followup.xml',
    ],
    # Demo files - only installed and updated in demo Mode
    'demo': [],
    # Asset Bundles
    'assets': {},
    # Hooks
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_init_hook': '',
}
