# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'ecoservice: Partner Account',
    'summary': 'New debit and credit account following a sequence per company for partner.',
    'category': 'Accounting',
    'version': '16.0.1.1.0',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice GbR',
    'maintainer': 'ecoservice GbR',
    'website': 'https://ecoservice.de/en_US/shop/product/automatic-debit-and-credit-number-49',
    # Odoo Apps Store
    'price': 630.00,
    'currency': 'EUR',
    'images': [
        'images/paracc_configuration.png',
    ],
    # Dependencies
    'depends': [
        'base',
        'account',
    ],
    # Data
    'data': [
        'views/res/config/settings/form.xml',
        'views/res/partner/form.xml',
        'views/res/partner/action.xml',
        'views/res/account/form.xml',
    ],
}
