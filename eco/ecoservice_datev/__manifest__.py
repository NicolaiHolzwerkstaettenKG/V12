# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    'name': 'DATEV',
    'summary': 'DATEV interface in accordance with offical docs.',
    'category': 'Accounting',
    'version': '16.0.1.2.0',
    'author': 'ecoservice GbR',
    'website': 'https://www.ecoservice.de',
    'license': 'OPL-1',
    'category': 'Base',
    'application': True,
    'installable': True,
    'support': 'datev@ecoservice.de',
    'price': 800.00,
    'currency': 'EUR',
    'images': [],
    'depends': [
        'base',
        'account',
        'l10n_de',
        'mail',
        'sale',
    ],
    'data': [
        # Order matters!
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account/move/form.xml',
        'views/datev/export/form.xml',
        'views/datev/export/tree.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/res/config/settings/form.xml',
    ],
}
