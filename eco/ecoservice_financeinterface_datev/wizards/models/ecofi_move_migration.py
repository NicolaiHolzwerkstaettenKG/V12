# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, exceptions, fields, models


class EcofiMoveMigration(models.TransientModel):
    _name = 'ecofi.move.migration'
    _description = (
        'Wizard to set the taxes and counter accounts for the DATEV export'
    )

    migrate_all_journal_item_from = fields.Date()
    migrate_all_journal_item_to = fields.Date()

    taxes_are_configured = fields.Boolean(
        required=True,
        help='Check this if you have configured the taxes with the correct tax'
             ' keys according to the guide or the official SKR Documentation.'
             "If you have checked 'Migrate account moves of all companies'"
             ' please make sure that you have configured the taxes for all'
             ' appropriate companies.',
    )
    accounts_are_configured = fields.Boolean(
        required=True,
        help='Check this if you have configured the accounts according to the'
             ' guide or the official SKR Documentation. If you have checked'
             " 'Migrate account moves of all companies' please make sure that"
             ' you have configured the accounts for all appropriate companies.',
    )

    companies = fields.Char()
    to_check_counter = fields.Integer()

    def action_migrate(self):
        date_from = self.migrate_all_journal_item_from
        date_to = self.migrate_all_journal_item_to

        if not date_from and date_to:
            raise exceptions.UserError(_(
                "please set also migrate all journal item from date"
            ))
        if date_from and not date_to:
            raise exceptions.UserError(_(
                "please set also migrate all journal item to date"
            ))
        if date_from and date_to:
            if date_from >= date_to:
                self.raise_user_error_from_date_to_date()

        if not (self.taxes_are_configured and self.accounts_are_configured):
            raise exceptions.UserError(_(
                "Both Checkboxes 'Taxes are configured' and 'Accounts are"
                " configured' must be checked in order to proceed!",
            ))

        sesu = self.sudo().with_context(logs={'to_check_counter': 0})

        companies = sesu._get_companies_with_skr() + self.env.company

        if not companies:
            return

        sesu._migrate_accounts(
            companies,
            date_from,
            date_to,
        )
        sesu._migrate_taxes(
            companies,
            date_from,
            date_to
        )

        return sesu._show_result(companies)

    def _get_companies_with_skr(self):
        skr = self._get_available_skr_charts()
        company_model = self.env['res.company']

        if not skr:
            return company_model

        companies = company_model.search([('chart_template_id', 'in', skr)])

        return companies

    def _get_available_skr_charts(self):
        skr03 = self.env.ref('l10n_de_skr03.l10n_de_chart_template', False)
        skr04 = self.env.ref('l10n_de_skr04.l10n_chart_de_skr04', False)

        return [skr.id for skr in [skr03, skr04] if skr]

    def _migrate_accounts(self, companies, date_from, date_to):
        journals = self.env['account.journal'].search([
            ('company_id', 'in', companies.ids),
        ])
        for journal in journals:
            handle_fn = '_handle_journal_{}'.format(journal.type)
            getattr(
                self.with_company(journal.company_id),
                handle_fn
            )(journal, date_from, date_to)

    def _migrate_taxes(self, companies, date_from, date_to):
        accounts_with_taxes = self.env['account.account'].search([
            ('datev_tax_ids', '!=', False),
            ('company_id', 'in', companies.ids),
        ])
        for account in accounts_with_taxes.with_context(active_test=False):
            if date_from and date_to:
                move_lines = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                ])
            else:
                move_lines = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('move_id.state', '=', 'posted'),
                ])

            move_lines = move_lines.filtered(
                lambda r:
                not r.move_id.vorlauf_id
                and not getattr(r.move_id, 'datev_export')
                and not getattr(r, 'datev_export')
            )
            move_lines.write({
                'ecofi_tax_id': account.datev_tax_ids[0].id,
            })
        if date_from and date_to:
            lines_with_taxes = self.env['account.move.line'].search([
                ('tax_ids', '!=', False),
                ('ecofi_tax_id', '=', False),
                ('company_id', 'in', companies.ids),
                ('move_id.state', '=', 'posted'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ])
        else:
            lines_with_taxes = self.env['account.move.line'].search([
                ('tax_ids', '!=', False),
                ('ecofi_tax_id', '=', False),
                ('company_id', 'in', companies.ids),
                ('move_id.state', '=', 'posted'),
            ])
        lines_with_taxes = lines_with_taxes.filtered(
            lambda r:
            not r.move_id.vorlauf_id
            and not getattr(r.move_id, 'datev_export')
            and not getattr(r, 'datev_export')
        )
        for line in lines_with_taxes.with_context(active_test=False):
            line.ecofi_tax_id = line.tax_ids[0]

    def _handle_journal_sale(self, journal, date_from, date_to):
        self._set_counter_account_from_invoice(journal, date_from, date_to)

    def _handle_journal_purchase(self, journal, date_from, date_to):
        self._set_counter_account_from_invoice(journal, date_from, date_to)

    def _handle_journal_cash(self, journal, date_from, date_to):
        self._set_counter_account_from_journal(journal, date_from, date_to)

    def _handle_journal_bank(self, journal, date_from, date_to):
        self._set_counter_account_from_journal(journal, date_from, date_to)

    def _handle_journal_general(self, journal, date_from, date_to):
        if date_from and date_to:
            moves = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'posted'),
            ])
        else:
            moves = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('state', '=', 'posted'),
            ])
        for move in moves:
            move_datev_export = getattr(move, 'datev_export')
            if move.vorlauf_id or move_datev_export:
                continue
            skip_invoice = False
            for line_id in move.line_ids:
                move_line_datev_export = getattr(line_id, 'datev_export')
                if move_line_datev_export:
                    skip_invoice = True
                    break
            if skip_invoice:
                continue

            # Fewer than two move lines? This is not valid according to
            # Double-Entry Accounting
            if len(move.line_ids) < 2:
                self.env.context['logs']['to_check_counter'] += 1
                move.write({
                    'ecofi_to_check': True,
                })

            # If the move has more than two lines we can check for the
            # amount of credit and debit accounts.
            # We could also check for the special case of exactly two move lines
            # but that would be more code with doubtful performance improvements
            credit_lines = move.line_ids.filtered('credit')
            debit_lines = move.line_ids.filtered('debit')

            # If there is only one line where the debit amount is set: use it.
            # Also true for len(move.line_ids) == 2
            if len(debit_lines) == 1:
                move.line_ids.write({
                    'ecofi_account_counterpart': debit_lines.account_id.id,
                })
            # Alternatively, if there is only one line where the credit amount
            # is set: Use this one instead
            elif len(credit_lines) == 1:
                move.line_ids.write({
                    'ecofi_account_counterpart': credit_lines.account_id.id,
                })
            else:
                accounts = move.line_ids.mapped('account_id')
                if len(accounts) == 2:
                    move.line_ids.write({
                        'ecofi_account_counterpart': accounts[0].id,
                    })
                # We can't do funny cases automatically (yet),
                # so the user has to do it manually
                else:
                    self.env.context['logs']['to_check_counter'] += 1
                    move.write({
                        'ecofi_to_check': True,
                    })

    def _set_counter_account_from_journal(self, journal, date_from, date_to):
        if date_from and date_to:
            moves = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'posted'),
            ])
        else:
            moves = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('state', '=', 'posted'),
            ])
        for move in moves:
            move_datev_export = getattr(move, 'datev_export')
            if move.vorlauf_id or move_datev_export:
                continue
            skip_invoice = False
            for line_id in move.line_ids:
                move_line_datev_export = getattr(line_id, 'datev_export')
                if move_line_datev_export:
                    skip_invoice = True
                    break
            if skip_invoice:
                continue
            move.set_main_account()

    def _set_counter_account_from_invoice(self, journal, date_from, date_to):
        if date_from and date_to:
            invoices = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'posted'),
            ])
        else:
            invoices = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('state', '=', 'posted'),
            ])
        if journal.type == 'sale':
            for invoice in invoices:
                move_datev_export = getattr(invoice, 'datev_export')
                if invoice.vorlauf_id or move_datev_export:
                    continue
                skip_invoice = False
                for line_id in invoice.line_ids:
                    move_line_datev_export = getattr(line_id, 'datev_export')
                    if move_line_datev_export:
                        skip_invoice = True
                        break
                if skip_invoice:
                    continue
                invoice.mapped('line_ids').write({
                    'ecofi_account_counterpart':
                        invoice.partner_id.property_account_receivable_id.id,
                })
        else:
            for invoice in invoices:
                move_datev_export = getattr(invoice, 'datev_export')
                if invoice.vorlauf_id or move_datev_export:
                    continue
                skip_invoice = False
                for line_id in invoice.line_ids:
                    move_line_datev_export = getattr(line_id, 'datev_export')
                    if move_line_datev_export:
                        skip_invoice = True
                        break
                if skip_invoice:
                    continue
                invoice.mapped('line_ids').write({
                    'ecofi_account_counterpart':
                        invoice.partner_id.property_account_payable_id.id,
                })

    def _show_result(self, companies):
        action = self.env.ref(
            'ecoservice_financeinterface_datev'
            '.action_ecofi_move_migration_result',
        ).read()[0]

        action['context'] = {
            'default_companies':
                ', '.join(companies.mapped('name')),
            'default_to_check_counter':
                self.env.context['logs']['to_check_counter'],
        }

        return action

    def raise_user_error_from_date_to_date(self):
        raise exceptions.UserError(_(
            'migrate all journal item from date is greater or equal then migrate all journal item to date'
        ))
