# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'Auto Datev Export',
    'summary': 'Generate CSV files and send them via mail based on a time interval.',
    'category': 'Accounting',
    'version': '16.0.1.0.1',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'price': 450.00,
    # Author
    'author': 'ecoservice',
    'website': 'https://ecoservice.de/',
    # Odoo Apps Store
    'support': 'financeinterface@ecoservice.de',
    # Dependencies
    'depends': [
        'ecoservice_financeinterface',  # eco/finace-interface
        'ecoservice_financeinterface_datev',  # eco/finace-interface
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'views/auto_datev_export_config.xml',
        'views/res_config_settings.xml'
    ],
}
