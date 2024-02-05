# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'eco_report.mixin']

    # region Fields
    account_invoice = fields.Html(
        string='Invoice (Top)',
    )
    account_refund = fields.Html(
        string='Refund (Top)',
    )
    account_invoice_bottom = fields.Html(
        string='Invoice (Bottom)',
    )
    account_refund_bottom = fields.Html(
        string='Refund (Bottom)',
    )
    amount_by_group = fields.Binary(
        string='Tax amount by group',
        compute='_compute_invoice_taxes_by_group',
        help='Edit Tax amounts if you encounter rounding issues.'
    )
    delivery_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Enter the delivery period (e.g. month) or the delivery date here.'
    )
    # endregion

    # region Compute Methods
    def _compute_dates(self):
        for rec in self:
            rec.report_compute_date = fields.Date.context_today(
                rec,
                fields.Datetime.from_string(rec.invoice_date or ''),
            )

    @api.depends(
        'line_ids.price_subtotal',
        'line_ids.tax_base_amount',
        'line_ids.tax_line_id',
        'partner_id',
        'currency_id'
    )
    def _compute_invoice_taxes_by_group(self):
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.amount_by_group = []
                continue

            lang_env = move.with_context(lang=move.partner_id.lang).env
            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered('tax_line_id')
            base_lines = move.line_ids.filtered('tax_ids')

            tax_group_mapping = defaultdict(lambda: {
                'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
            })

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * \
                    (base_line.amount_currency if base_line.currency_id else base_line.balance)

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_group_id]
                    if base_line not in tax_group_vals['base_lines']:
                        tax_group_vals['base_amount'] += base_amount
                        tax_group_vals['base_lines'].add(base_line)

            # Compute tax amounts.
            for tax_line in tax_lines:
                tax_amount = balance_multiplicator * \
                    (tax_line.amount_currency if tax_line.currency_id else tax_line.balance)
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals['tax_amount'] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                amount_by_group.append((
                    tax_group.name,
                    tax_group_vals['tax_amount'],
                    tax_group_vals['base_amount'],
                    formatLang(
                        lang_env, tax_group_vals['tax_amount'], currency_obj=move.currency_id),
                    formatLang(
                        lang_env, tax_group_vals['base_amount'], currency_obj=move.currency_id),
                    len(tax_group_mapping),
                    tax_group.id
                ))
            move.amount_by_group = amount_by_group
    # endregion

    # region Onchange Methods
    @api.onchange('delivery_date')
    def onchange_delivery_date(self):
        if self.move_type not in ['out_invoice', 'out_refund']:
            return
        if not self.create_date:
            return
        elif self.delivery_date:
            self.date = self.delivery_date
        elif self.invoice_date:
            self.date = self.invoice_date
        else:
            self.date = self.create_date.date()

    @api.onchange('partner_id')
    def get_template_text(self):
        # While changing partner: change the text according to partner's language
        # and do not reset this if text is written manually

        if self.partner_id:
            field_xml_list = []
            if (
                not self.account_invoice
                or self.account_invoice == '<p><br></p>'
            ):
                field_xml_list.append((
                    'account_invoice',
                    'ecoservice_german_documents_invoice.account_invoice_text',
                ))

            if (
                not self.account_invoice_bottom
                or self.account_invoice_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'account_invoice_bottom',
                    'ecoservice_german_documents_invoice.account_invoice_text_bottom',
                ))

            if (
                not self.account_refund
                or self.account_refund == '<p><br></p>'
            ):
                field_xml_list.append((
                    'account_refund',
                    'ecoservice_german_documents_invoice.account_refund_text',
                ))

            if (
                not self.account_refund_bottom
                or self.account_refund_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'account_refund_bottom',
                    'ecoservice_german_documents_invoice.account_refund_text_bottom',
                ))

            vals = self.env['text.template.config'].get_template_text(
                self.partner_id.lang,
                field_xml_list,
            )
            self.update(vals)

    # Check if Customer Address Field in Settings True or False
    def get_value_customer_address(self):
        return self.env.company.delivery_address

    # endregion

    # region CRUD Methods
    @api.model_create_multi
    def create(self, vals_list):
        fields_name = ['account_invoice', 'account_refund']
        invoice_vals_list = []

        for value in vals_list:
            values = self.is_html_field_empty(
                vals=value,
                fields=fields_name
            )
            invoice_vals_list.append(values)

        invoices = super(AccountMove, self).create(invoice_vals_list)
        for invoice in invoices:
            invoice.get_template_text()
        return invoices

    def write(self, values):
        fields_name = ['account_invoice', 'account_refund']
        values = self.is_html_field_empty(
            vals=values,
            fields=fields_name
        )
        return super(AccountMove, self).write(values)
    # endregion

    # region Business Methods
    def _get_prefixes(self):
        # Throw exception if there are records that should not be printed
        if any(not move.is_invoice() for move in self):
            raise UserError(_('Only invoices could be printed.'))

        invoice = any('invoice' in r.move_type for r in self)
        refund = any('refund' in r.move_type for r in self)

        return [
            x for x
            in [
                invoice and _('Invoice'),
                refund and _('Refund'),
            ]
            if x
        ]

    def _get_reconciled_info_json_values(self):
        self.ensure_one()
        reconciled_vals = []
        for partial, amount, counterpart_line in self._get_reconciled_invoices_partials()[0]:
            reconciled_vals.append({
                'partial_id': partial.id,
                'amount': amount,
                'date': counterpart_line.date,
            })
        return reconciled_vals

    def is_down_payment(self):
        """Return if the current invoice has down invoice lines."""
        return self.mapped('invoice_line_ids').filtered(
            lambda line: line.is_down_payment()
        )
    # endregion

    @api.model
    def check_if_remove_html_tags(self, html_field):

        if hasattr(self.env['res.company'], 'remove_html_tags'):
            raw_text = self.env['res.company'].remove_html_tags(html_field)
        else:
            raw_text = html_field

        return raw_text
