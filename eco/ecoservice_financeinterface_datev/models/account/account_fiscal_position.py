# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import api, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    # region CRUD

    def write(self, vals):
        destination_accounts = self._get_destination_accounts(
            vals.get('account_ids'),
        )
        if 'vat_required' in vals:
            if destination_accounts:
                destination_accounts.write({'datev_vat_handover': vals['vat_required']})
            # Note: account_ids._name == 'account.fiscal.position.account'
            self.mapped('account_ids.account_dest_id').write(
                {'datev_vat_handover': vals['vat_required']}
            )
        else:
            if destination_accounts:
                # TODO clarify: does this even make sense?
                for fiscal_position in self:
                    destination_accounts.write(
                        {'datev_vat_handover': fiscal_position.vat_required}
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._create_vat_required(vals)
        return super().create(vals_list)

    def _create_vat_required(self, vals):
        if not vals.get('vat_required'):
            return

        accounts = vals.get('account_ids')
        destination_accounts = self._get_destination_accounts(accounts)
        if destination_accounts:
            destination_accounts.write({'datev_vat_handover': True})

    # endregion

    # region Business Methods

    def _get_destination_accounts(self, account_ids: list):
        """
        Take account.fiscal.position.account and extract the destinations.

        :param account_ids: A list of account.fiscal.position.account
        :return: A recordset of the destination accounts. Can be empty.
        """
        if not isinstance(account_ids, list):
            account_ids = []

        account_model = self.env['account.account']
        res_account_ids = []
        for account in account_ids:
            # account_ids is a list of commands to change the one2many linked
            # records. We only work on (0, 0,  { values })
            # and (1, ID, { values })! Existing lines can't be linked to a
            # new record, all deleted lines could be ignored
            if (
                len(account) > 2
                and account[2]
                and isinstance(account[2], dict)
                and account[2].get('account_dest_id')
            ):
                res_account_ids.append(account[2]['account_dest_id'])
        return account_model.browse(res_account_ids)

    # endregion
