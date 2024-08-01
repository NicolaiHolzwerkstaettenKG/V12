# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from collections import defaultdict

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    visible_account_counterpart = fields.Boolean(
        compute='_set_visible_account_counterpart'
    )

    def _set_visible_account_counterpart(self):
        if self.user_has_groups('base.group_no_one') or self.ecofi_manual:
            self.visible_account_counterpart = True
        else:
            self.visible_account_counterpart = False

    @api.ecofi_validate('validate_account_counter_account')
    def _validate_account_counter_account(self):
        """Test if the move account counterparts are set correct."""

        # There is a possibility to post account moves w/o move lines
        moves_to_validate = self.filtered('line_ids')
        # Check if a move should get additional data before the check
        moves_to_validate.line_ids.filtered(
            lambda r: not r.ecofi_account_counterpart
        ).move_id.set_main_account()
        for move in moves_to_validate:
            count = 0
            result = {}

            for line in move.line_ids.filtered(
                lambda l: l.display_type not in ['line_section', 'line_note']  # Skip sections and notes
            ):
                if not line.account_id or not line.ecofi_account_counterpart:
                    count += 1
                    continue

                counter_account_id = line.ecofi_account_counterpart.id
                if counter_account_id not in result:
                    result[counter_account_id] = defaultdict(int)

                equal_accounts = line.account_id.id == counter_account_id
                key = 'check' if not equal_accounts else 'real'
                result[counter_account_id][key] += line.debit - line.credit

            error_msg = []
            if count:
                error_msg.append(
                    _(
                        '{count} lines of move {move_name} ({move_id}) do not '
                        'have both accounts, an account and a counter account, '
                        'defined!'
                    ).format(
                        count=count,
                        move_name=move.name,
                        move_id=move.id,
                    )
                )
            if any(
                abs(value['check'] + value['real']) > 10 ** -4
                for value in result.values()
            ):
                error_msg.append(
                    _(
                        'The difference between account and counter account '
                        'debit/credit sum for move {move_name} ({move_id}) is '
                        'not zero!'
                    ).format(
                        move_name=move.name,
                        move_id=move.id,
                    )
                )
            if error_msg:
                raise exceptions.ValidationError(
                    '\n\n'.join(error_msg)
                )

    def _post(self, soft=True):
        self.set_main_account()
        self.set_ecofi_tax_id()
        result = super()._post(soft=soft)
        # only if a new company account has been generated.
        self.set_main_account()
        return result

    def button_draft(self):
        if self.vorlauf_id:
            raise UserError(_('This invoice has been exported and cannot be reset to draft.'))
        else:
            return super(AccountMove, self).button_draft()

    def set_ecofi_tax_id(self):
        for line in self.invoice_line_ids:
            line.ecofi_tax_id = line.tax_ids

    def set_main_account(self) -> None:
        """
        Set the main account of the corresponding account_move.

        How the main account is calculated (tax lines are ignored):

        1. In an invoice the main account is always the creditor / debtor.
        2. In bank and cash journals the account is the one in the journal.
        3. Analyse the number of debit and credit lines:
            a. 1 debit, n credit lines: the debit line account
            b. m debit, 1 credit lines: the credit line account
            c. 1 debit, 1 credit lines: the first line account
        """
        for move in self.filtered(lambda r: r.line_ids):
            if not (
                move._set_global_counter_account_from_journal()
                or move._set_global_counter_account_from_lines()
                or move._set_local_counter_account()
            ):
                move.ecofi_to_check = True
                move.ecofi_manual = True

    def _account_from_general(self):
        journal = self.journal_id
        if journal != self.env.company.currency_exchange_journal_id:
            return None

        accounts = set(self.line_ids.filtered(
            lambda r: r.account_id == journal.default_account_id
        ).mapped('account_id'))
        return journal.default_account_id if len(accounts) == 1 else None

    def _account_from_purchase(self):
        return self.partner_id.property_account_payable_id

    def _account_from_sale(self):
        return self.partner_id.property_account_receivable_id

    def _account_from_bank(self):
        return self.journal_id.default_account_id

    def _account_from_cash(self):
        return self.journal_id.default_account_id

    def _set_global_counter_account_from_journal(self) -> bool:
        fn_counter_account = getattr(
            self,
            f'_account_from_{self.journal_id.type}',
            lambda *_: None,
        )
        counter_account = fn_counter_account()
        if counter_account:
            self.line_ids.ecofi_account_counterpart = counter_account
            return True
        return False

    def _set_global_counter_account_from_lines(self) -> bool:
        # Ignore tax lines because tax accounts should never be counter accounts
        tax_lines = self.line_ids.filtered(
            lambda l: l.account_id.is_tax_account()
        )
        debit_lines = self.line_ids.filtered('debit') - tax_lines
        credit_lines = self.line_ids.filtered('credit') - tax_lines
        debit_accounts = debit_lines.mapped('account_id')
        credit_accounts = credit_lines.mapped('account_id')

        if len(debit_accounts) == 1:
            self.line_ids.ecofi_account_counterpart = debit_accounts
            return True

        if len(credit_accounts) == 1:
            self.line_ids.ecofi_account_counterpart = credit_accounts
            return True

        # if both debit and credit lines are zero and max lines are 2
        # set the contra account to the first line account
        if (
            len(debit_accounts) == 0
            and len(credit_accounts) == 0
            and len(self.line_ids) == 2
        ):
            self.line_ids.ecofi_account_counterpart = self.line_ids[0].account_id

        return False

    def _set_local_counter_account(self) -> bool:
        try:
            accounts = self._handle_group(self.line_ids)
        except (IndexError, StopIteration, ValueError):
            self.ecofi_to_check = True
            return False

        if len(accounts) != len(self.line_ids):
            return False

        for account, line in zip(accounts, self.line_ids):
            line.ecofi_account_counterpart = account

        return True

    @api.model
    def _handle_group(self, lines):
        if not lines:
            return []

        first_line = lines[0]

        counter = first_line.account_id
        amount = first_line.debit - first_line.credit
        ret = [counter]

        if amount == 0:
            return ret

        if amount > 0:
            return ret + self._handle_credit_sub_group(lines[1:], amount, counter)

        return ret + self._handle_debit_sub_group(lines[1:], amount, counter)

    @api.model
    def _handle_credit_sub_group(self, lines, amount, counter):
        current_line = lines[0]
        amount -= current_line.credit
        ret = [counter]

        if amount < 0:
            raise ValueError

        if amount == 0:
            return ret + self._handle_group(lines[1:])

        return ret + self._handle_credit_sub_group(lines[1:], amount, counter)

    @api.model
    def _handle_debit_sub_group(self, lines, amount, counter):
        current_line = lines[0]
        amount += current_line.debit
        ret = [counter]

        if amount > 0:
            raise ValueError

        if amount == 0:
            return ret + self._handle_group(lines[1:])

        return ret + self._handle_debit_sub_group(lines[1:], amount, counter)
