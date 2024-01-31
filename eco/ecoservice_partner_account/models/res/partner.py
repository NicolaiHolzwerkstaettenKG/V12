# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models

ACCOUNT_TYPE_PAYABLE: str = 'liability_payable'
ACCOUNT_TYPE_RECEIVABLE: str = 'asset_receivable'


# noinspection PyAttributeOutsideInit,PyTypeChecker
class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_custom_payable = fields.Boolean(
        related='property_account_payable_id.is_partner_account',
        string='Custom Payable',
    )

    has_custom_receivable = fields.Boolean(
        related='property_account_receivable_id.is_partner_account',
        string='Custom Receivable',
    )

    @property
    def company(self):
        return self.company_id or self.env.company

    # region View

    def action_create_payable_account(self) -> bool:
        """
        Create a payable account from the GUI.

        Creating an account from the GUI always counts as manual creation.
        Thus any automatic account creation setting is ignored. The sharing
        setting is taken into account though.
        """
        self.ensure_one()
        self.create_accounts([ACCOUNT_TYPE_PAYABLE])
        return True

    def action_create_receivable_account(self) -> bool:
        """
        Create a receivable account from the GUI.

        Creating an account from the GUI always counts as manual creation.
        Thus any automatic account creation setting is ignored. The sharing
        setting is taken into account though.
        """
        self.ensure_one()
        self.create_accounts([ACCOUNT_TYPE_RECEIVABLE])
        return True

    # endregion

    def create_accounts(self, account_types: list = []) -> bool:
        for partner in self:
            account_types = account_types or partner.default_account_types()
            partner._create_accounts(account_types)
            partner._share_partner_accounts(account_types)
        return True

    def _share_partner_accounts(self, account_types):
        for account_type in account_types:
            self._share_partner_account(account_type)

    def _share_partner_account(self, account_type):
        if not self.company.shared_partner_accounts:
            return

        companies = self.company
        if self.company.shared_partner_accounts:
            companies = self.company.search([
                ('shared_partner_accounts', '=', True)
            ])

        ftype = (
            'payable'
            if account_type == ACCOUNT_TYPE_PAYABLE else
            'receivable'
        )
        fname = f'property_account_{ftype}_id'
        main_code = getattr(self, fname).code

        for company in companies:
            partner = self.with_company(company=company)
            field = getattr(partner, fname)

            if not field.is_partner_account:
                partner._create_account(account_type, main_code)
                continue

            field.write({
                'code': main_code,
            })

    def _create_accounts(self, account_types: list):
        self.ensure_one()

        for account_type in account_types:
            self._create_account(account_type)

    def _create_account(self, account_type: str, code=None):
        self.ensure_one()

        ftype = (
            'payable'
            if account_type == ACCOUNT_TYPE_PAYABLE else
            'receivable'
        )
        fname = f'property_account_{ftype}_id'
        account = getattr(self, fname)

        if account.is_partner_account:
            return account

        if not code:
            code = self.company.next_account_code(account_type)

        new_account = account.create({
            'company_id': self.company.id,
            'is_partner_account': True,
            'currency_id': self.company.currency_id.id,
            'code': code,
            'name': self.commercial_partner_id.name,
            'reconcile': True,
            'account_type': account_type,
            'tag_ids': [(6, 0, account.tag_ids.ids)]
        })

        result = {}
        result[fname] = new_account.id

        if (
            self.company.partner_ref_source == account_type
            and not self.ref
        ):
            result['ref'] = new_account.code

        self.write(result)

    def default_account_types(self) -> list:
        self.ensure_one()

        # When creating a new partner, supplier and customer rank is always
        # False. Checking for them to decide account types is pointless.
        return [
            ACCOUNT_TYPE_RECEIVABLE,
            ACCOUNT_TYPE_PAYABLE,
        ]
