# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'DATEV Masterdata',
    'summary': 'Lets you export your accounting master data',
    'category': 'Accounting',
    'version': '16.0.1.2.2',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice GbR',
    'website': 'https://ecoservice.de/shop/product/odoo-datev-export-53',
    'live_test_url': 'https://www.ecoservice.de/odoo-demo',
    # Odoo Apps Store
    'price': 550.00,
    'currency': 'EUR',
    'support': 'financeinterface@ecoservice.de',
    # Dependencies
    'depends': [
        'account',
        'base',

        'ecoservice_financeinterface',  # eco/finance-interface
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'data/datev_export_data.xml',
        'views/datev_export.xml',
        'wizards/export_ecofi_datev_export.xml',
    ],
}
