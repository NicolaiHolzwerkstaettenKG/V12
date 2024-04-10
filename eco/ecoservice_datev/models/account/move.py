# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import shutil
import uuid
import re

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

    def datev_attachments(self, exportdir: str, generate_pdf=False, attachments=False) -> list:
        """Get all move related attachments.

        Args:
            exportdir (str): Export path
            generate_pdf (bool, optional):
                Generate invoice like attachment. Defaults to False.
            attachments (recordset(ir.attachment), optional)

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

        if not attachments:
            attachments = self.env['ir.attachment'].sudo()
            attachments = attachments.search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', self.id),
                ('store_fname', '!=', False)
            ])
        attachments = attachments.filtered(lambda x: x.datev_compatible())
        filestore = attachments._filestore()

        files = {}
        for attachment in attachments:
            skip = False
            fpath = f'{filestore}/{attachment.store_fname}'
            fname = f'{self.id}_{attachment.display_name}'
            if invoice and invoice.id == attachment.id:
                fname = f'{self.id}.pdf'
            fname = self.secure_fname(fname=fname)
            if fname not in files:
                files[fname] = {
                    'fpath': fpath,
                    'checksum': attachment.checksum,
                }
            else:
                fname_counter = 2
                new_fname = fname
                while not skip and new_fname in files:
                    # skip this file if the files are the same
                    if files[new_fname]['checksum'] == attachment.checksum or files[new_fname]['fpath'] == fpath:
                        skip = True
                    else:
                        fname_split = fname.split('.', 1)
                        if len(fname_split) == 2:
                            new_fname = '%s_%s.%s' % (fname_split[0], fname_counter, fname_split[1])
                        else:
                            new_fname = '%s_%s' % (fname, fname_counter)
                        fname_counter += 1
                if not skip:
                    fname = new_fname
                    files[fname] = {
                        'fpath': fpath,
                        'checksum': attachment.checksum,
                    }
            if not skip:
                epath = f'{exportdir}/{fname}'
                shutil.copyfile(src=fpath, dst=epath)
        return [fname for fname in files]

    def secure_fname(self, fname: str) -> str:
        # remove all dots except the last one
        fname = fname.lower().replace('.', '_', fname.count('.') - 1)
        # change frequently occurring characters to their permitted equivalent
        fname = fname.replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe').replace('ß', 'ss')
        # remove all characters that are not in a strict character set
        fname = re.sub(r'[^a-z0-9.]', '_', fname)
        # remove double _ to single _ until only single _ are left
        text_len = len(fname)
        changed = True
        while changed:
            fname = fname.replace('__', '_')
            changed = text_len > len(fname)
            text_len = len(fname)
        return fname

    def datev_invoice_lines(self):
        return self.invoice_line_ids.filtered(
            lambda x: x.datev_relevant()
        )
