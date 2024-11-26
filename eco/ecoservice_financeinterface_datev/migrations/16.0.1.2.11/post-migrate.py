# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import datetime
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    target_date = datetime.datetime(2024, 1, 1)
    bank_journal = env['account.journal'].search([('type', '=', 'bank')])
    moves = env['account.move'].search([
        ('create_date', '>=', target_date),
        ('state', '=', 'posted'),
        ('journal_id', 'in', bank_journal.ids),
    ])
    for move in moves:
        account_codes = []
        for line in move.line_ids:
            account_codes.append(line.account_id.code)
        account_counterpart_code = move.line_ids[0].ecofi_account_counterpart.code or None
        if move.vorlauf_id:
            continue
        if account_counterpart_code not in account_codes:
            _logger.info('invoice name: %s', move.name)
            move.set_main_account()
