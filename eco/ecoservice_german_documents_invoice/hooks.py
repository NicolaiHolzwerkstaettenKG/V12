# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fi_installed = env['ir.module.module'].search([
        ('name', '=', 'ecoservice_financeinterface'),
        ('state', '=', 'installed')
    ])
    if fi_installed:
        try:
            env['account.move'].set_delivery_date_exists(True)
        except Exception as e:
            _logger.error("An error occurred: %s", str(e))


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fi_installed = env['ir.module.module'].search([
        ('name', '=', 'ecoservice_financeinterface'),
        ('state', '=', 'installed')
    ])
    if fi_installed:
        env['account.move'].set_delivery_date_exists(False)
