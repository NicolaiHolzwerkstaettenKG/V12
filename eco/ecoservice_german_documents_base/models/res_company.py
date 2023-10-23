# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # region Fields
    chief_executive_officer = fields.Text()
    report_table_position = fields.Boolean(
        string='Show line item number in printed documents',
        default=True,
    )
    report_table_position_continuous = fields.Boolean(
        string='Share continuous line item numbers across all sections',
        default=True,
    )
    standard_document_language = fields.Selection(
        selection='_get_all_languages',
    )
    report_footer_as_image = fields.Boolean(
        default=False,
    )
    report_footer_image = fields.Binary()
    # endregion

    # region Business Methods
    def get_bank_accounts(self):
        if 'account.journal' not in self.env:
            return []

        bank_journal = []
        journals = self.env['account.journal'].search(
            [
                ('company_id', '=', self.id),
                ('type', 'in', ['bank']),
                ('bank_id', '!=', False),
                ('show_bank_data_invoice', '=', True),
            ],
            limit=2,
        )

        if not journals:
            return []

        for journal in journals:
            bank_journal.append(journal)

        return bank_journal

    def _get_all_languages(self):
        return self.env['res.lang'].get_installed()

    def get_footer_as_image(self):
        if self.report_footer_image and self.report_footer_as_image:
            return True
        return False

    # endregion
