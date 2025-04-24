# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from decimal import Decimal
from odoo import _, api, exceptions, fields, models


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = [
        'account.move.line',
        'ecofi.validation.mixin',
    ]

    # region Fields

    ecofi_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Move Tax',
    )
    # the field will be deleted later because it is in the ecoservice_financeinterface_datev module
    ecofi_account_counterpart = fields.Many2one(
        string='Account Counterpart',
        comodel_name='account.account',
        ondelete='restrict',
    )
    line_ref = fields.Char()
    eco_balance = fields.Monetary()
    # endregion

    # region Constrains

    @api.constrains('tax_ids')
    def _check_tax_ids(self):
        for line in self.filtered(lambda l: l.company_id.uses_skr()):
            if len(line.tax_ids) > 1:
                raise exceptions.ValidationError(_(
                    'Error! There can only be one tax per invoice line.'
                ))

    # endregion

    # region CRUD

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tax_ids = vals.get('tax_ids') or []  # tax_ids can be False
            if not vals.get('ecofi_tax_id') and tax_ids and tax_ids[0][2]:
                # account.payment transfers the actual ids in a set
                vals['ecofi_tax_id'] = list(tax_ids[0][2])[0]
        return super().create(vals_list)

    # endregion

    # region Business Methods

    def get_tax(self):
        """
        Return the used tax.
        """
        self.ensure_one()
        return (
            self.tax_ids
            or self.ecofi_tax_id
            or self.env['account.tax']
        )

    def get_tax_repartition_line_ids(self):
        """Tax reparation lines"""
        tax = self.get_tax()
        if self.is_refund:
            return tax.refund_repartition_line_ids
        return tax.invoice_repartition_line_ids

    def get_tax_multiplier(self):
        """Tax multiplier"""
        tax = self.get_tax()
        tax_repartitions = self.get_tax_repartition_line_ids()
        if tax_repartitions and len(tax_repartitions) > 2:
            # Steuern die einen Buchungssatz mit mehreren Steuern erzeugen,
            # sollen auf 0 gesetzt werden. Aufgabe 110719
            return 1
        return 1 + (Decimal(tax.amount) / 100)

    def _ecofi_validations_enabled(self):
        return self.move_id._ecofi_validations_enabled()

    def name_get(self):
        if self.env.context.get('counterpart_name'):
            result = []
            for line in self:
                if line.ref:
                    result.append(
                        (line.id, (line.name or '') + ' (' + line.ref + ')'),
                    )
                else:
                    result.append((line.id, line.name))
            return result
        return super().name_get()

    @api.ecofi_validate('validate_tax_count')
    def _validate_tax_count(self):
        """
        Check if there is at most one tax in the line.
        """

        self.ensure_one()

        is_valid = len(self.tax_ids) <= 1
        if not is_valid:
            raise exceptions.ValidationError(_('More than one tax specified!'))

    # endregion
