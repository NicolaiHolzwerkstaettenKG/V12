# Part of Odoo. Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE at the root directory of this module for full copyright and licensing details.

{
    'name': 'DATEV Import',
    'summary': 'This module allows you to import accounting entries.',
    'version': '16.0.1.0.12',
    'author': 'ecoservice',
    'website': 'https://ecoservice.de/shop/product/odoo-datev-export-53',
    'live_test_url': 'https://www.ecoservice.de/odoo-demo',
    'support': 'financeinterface@ecoservice.de',
    'license': 'OPL-1',
    'category': 'Accounting',
    # Odoo Apps Store
    'price': 650.00,
    'currency': 'EUR',
    'images': [
        'images/main_screenshot.gif',
    ],
    'depends': [
        'base',
        'account',
        'ecoservice_financeinterface',
        'ecoservice_financeinterface_datev',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/import_datev_sequence.xml',
        'views/account_account.xml',
        'views/import_datev.xml',
        'views/import_datev_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
