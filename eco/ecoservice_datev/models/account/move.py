# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import shutil
import uuid

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    datev_export = fields.Many2one(
        comodel_name='datev.export',
        readonly=True,
        copy=False,
        help=(
            'The record was exported to the accountant and/or tax office. '
            'It thereby shall no longer be modified under any circumstances.'
        )
    )

    uuid4 = fields.Char(
        copy=False,
        readonly=True,
    )  # Required for DATEV document links

    _sql_constraints = [
        (
            'uuid4_uniq',
            'unique(uuid4)',
            _('uuid4 be unique!'),
        ),
    ]

    def get_uuid4(self):
        if not self.uuid4:
            self.uuid4 = uuid.uuid4()
        return self.uuid4

    def button_draft(self):
        return super(
            AccountMove,
            self.filtered(lambda x: not x.datev_export)
        ).button_draft()

    def _compute_show_reset_to_draft_button(self):
        super(AccountMove, self)._compute_show_reset_to_draft_button()
        for move in self.filtered(lambda m: m.datev_export):
            move.show_reset_to_draft_button = False

    def datev_attachments(self, exportdir: str, generate_pdf=False) -> list:
        """Get all move related attachments.

        Args:
            exportdir (str): Export path
            generate_pdf (bool, optional):
                Generate invoice like attachment. Defaults to False.

        Returns:
            list: List of all move related attachments
        """
        if generate_pdf:
            self.env['ir.actions.report']._render_qweb_pdf(
                report_ref='account.account_invoices',
                res_ids=self.ids,
            )

        report_action = self.env['ir.actions.report'].sudo()
        invoice = report_action._get_report_from_name(
            report_name='account.report_invoice',
        ).retrieve_attachment(record=self)

        attachments = self.env['ir.attachment'].sudo()
        filestore = attachments._filestore()

        attachments = attachments.search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('store_fname', '!=', False)
        ])
        attachments = attachments.filtered(lambda x: x.datev_compatible())

        files = []
        for attachment in attachments:
            fpath = f'{filestore}/{attachment.store_fname}'
            fname = f'{self.id}_{attachment.display_name}'
            if invoice and invoice.id == attachment.id:
                fname = f'{self.id}.pdf'
            fname = self.secure_fname(fname=fname)
            epath = f'{exportdir}/{fname}'

            if fname in files:
                # Prevent duplicate files
                continue

            files.append(fname)
            shutil.copyfile(src=fpath, dst=epath)
        return files

    def invalid_fname_chars(self) -> list:
        return ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '!', '?']

    def secure_fname(self, fname: str) -> str:
        res = ''
        for c in fname:
            if c in self.invalid_fname_chars():
                continue
            res += c
        return res.encode('ascii', errors='ignore').decode('ascii')

    def datev_invoice_lines(self):
        return self.invoice_line_ids.filtered(
            lambda x: x.datev_relevant()
        )
