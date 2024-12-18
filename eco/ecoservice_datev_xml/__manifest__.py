# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    'name': 'DATEV Document Transfer',
    'summary': 'DATEV XML interface in accordance with offical docs.',
    'category': 'Accounting',
    'version': '16.0.1.1.1',
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
    'external_dependencies': {
        'python': ['xmlschema'],
    },
    'depends': [
        'base',
        'account',
        'product',
        'sale',

        'ecoservice_datev',
    ],
    'data': [],
}
