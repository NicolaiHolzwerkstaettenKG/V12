# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, exceptions, fields, models


class EcofiSetAccountCounterpart(models.TransientModel):
    _name = "ecofi.set.account.counterpart"
    _description = "Wizard to set the account counterpart for move lines"

    bank_journals = fields.Boolean(
        string="Set account counterpart for bank journals",
    )

    cash_journals = fields.Boolean(
        string="Set account counterpart for cash journals",
    )

    def action_set_account_counterpart(self):
        journals = []
        if not (self.bank_journals or self.cash_journals):
            raise exceptions.UserError(
                _(
                    "At least one of the checkboxes 'Set account counterpart for bank"
                    " journals' and 'Set account counterpart for cash journals' must be"
                    " checked in order to proceed!",
                )
            )

        if self.bank_journals:
            self.env.cr.execute(
                """
                SELECT id, default_account_id
                FROM account_journal
                WHERE type = 'bank'
                """
            )
            journals += self.env.cr.fetchall()

        if self.cash_journals:
            self.env.cr.execute(
                """
                SELECT id, default_account_id
                FROM account_journal
                WHERE type = 'cash'
                """
            )
            journals += self.env.cr.fetchall()

        for journal_id, account_id in journals:
            if account_id:
                self.env.cr.execute(
                    """
                UPDATE account_move_line
                SET ecofi_account_counterpart = %s
                WHERE journal_id = %s
                """,
                    (account_id, journal_id),
                )
