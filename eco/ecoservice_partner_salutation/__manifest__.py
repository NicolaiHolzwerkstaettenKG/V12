# Extension of Odoo. Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE at the root directory of this module for full copyright and licensing details.
{
    # App Information
    'name': 'Partner Salutation',
    'summary': 'Adds a salutation to the partner title.',
    'category': 'Base',
    'version': '16.0.1.0.0',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://www.ecoservice.de',
    # Dependencies
    'depends': [
        'base',
    ],
    # Data
    'data': [
        'static/src/sql/de.sql',
        'data/res_partner_data.xml',
        'views/res_partner_view.xml',
    ],
}
