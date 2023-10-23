# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    'name': 'Financeinterface CSV/XML connector',
    'summary': 'Attach documents to your CSV export via XML export.',
    'category': 'Accounting',
    'version': '16.0.1.0.0',
    'author': 'ecoservice GbR',
    'website': 'https://www.ecoservice.de',
    'license': 'OPL-1',
    'category': 'Base',
    'application': False,
    'installable': True,
    'auto_install': True,
    'support': 'datev@ecoservice.de',
    'images': [],
    'external_dependencies': {},
    'depends': [
        'ecoservice_datev',
        'ecoservice_datev_xml',
        'ecoservice_financeinterface',
        'ecoservice_financeinterface_datev',
    ],
    'data': [
        'views/ecofi/form.xml',
    ],
}
