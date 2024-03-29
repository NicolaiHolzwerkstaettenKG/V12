# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models

ACCOUNT_TYPE_PAYABLE: str = 'liability_payable'
ACCOUNT_TYPE_RECEIVABLE: str = 'asset_receivable'


class AccountMove(models.Model):
    _inherit = 'account.move'

    def check_partner_accounts_default(self, default_account):
        rec_pay_default_value = self.env['ir.property'].search(
            [
                ('name', '=', default_account),
                ('res_id', '=', False)
            ]
        )
        rec_pay_default_value_reference = int(rec_pay_default_value.value_reference.split(',')[1])
        is_account_default = True
        if default_account == 'property_account_receivable_id':
            if not rec_pay_default_value_reference == self.partner.property_account_receivable_id.id:
                is_account_default = False
        elif default_account == 'property_account_payable_id':
            if not rec_pay_default_value_reference == self.partner.property_account_payable_id.id:
                is_account_default = False
        else:
            is_account_default = True

        return is_account_default

    @property
    def company(self):
        return self.company_id or self.env.company

    @property
    def partner(self):
        return self.with_company(self.company).partner_id

    def _post(self, soft=True):
        for move in self:
            account_type = move.get_account_type()
            move.generate_partner_account(account_type)
            move.update_move_lines(account_type)
        return super()._post(soft=soft)

    def get_account_type(self) -> str:
        self.ensure_one()
        account_type = ''
        if self.move_type.startswith('out_'):
            account_type = ACCOUNT_TYPE_RECEIVABLE
        elif self.move_type.startswith('in_'):
            account_type = ACCOUNT_TYPE_PAYABLE
        return account_type

    def generate_partner_account(self, account_type=None):
        self.ensure_one()
        if account_type is None:
            # fallback for modules that override the old version of this method
            account_type = self.get_account_type()
        if account_type and self.company.partner_account_generate_automatically:
            if (
                    account_type == ACCOUNT_TYPE_RECEIVABLE
                    and self.check_partner_accounts_default('property_account_receivable_id')
            ):
                self.partner.create_accounts([account_type])
            elif (
                    account_type == ACCOUNT_TYPE_PAYABLE
                    and self.check_partner_accounts_default('property_account_payable_id')
            ):
                self.partner.create_accounts([account_type])

    def update_move_lines(self, account_type: str) -> None:
        self.ensure_one()
        if account_type:
            ftype = (
                'payable'
                if account_type == ACCOUNT_TYPE_PAYABLE else
                'receivable'
            )
            self.line_ids.filtered(
                lambda l: l.account_type == account_type,
            ).account_id = getattr(self.partner, f'property_account_{ftype}_id')
