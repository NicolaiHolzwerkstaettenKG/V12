# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import shutil
import tempfile
import uuid

from odoo import _, exceptions, fields, models


class DatevExport(models.Model):
    _name = 'datev.export'
    _description = 'DATEV Export'
    _order = 'date_from DESC'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default='DATEV Export')
    type = fields.Selection(  # noqa: A003
        string='Type',
        selection=[],
        required=True,
    )

    date_from = fields.Date(required=True,)
    date_to = fields.Date(required=True,)
    generated = fields.Boolean(
        default=False,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    archive_id = fields.Many2one(
        string='File',
        comodel_name='ir.attachment',
        readonly=True,
    )
    uuid4 = fields.Char(readonly=True)

    def moves(self):
        return self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('amount_total', '!=', 0),
            ('company_id', '=', self.company_id.id),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('datev_export', '=', False),
            ('move_type', 'in', [
                'out_invoice',
                'out_refund',
                'in_invoice',
                'in_refund'
            ]),
        ])

    def reset(self) -> None:
        shutil.rmtree(
            f'{tempfile.gettempdir()}/datev/export',
            ignore_errors=True,
        )
        self.env['account.move'].search([
            ('datev_export', '=', self.id),
        ]).with_context(
            bypass_legal_revision=True
        ).datev_export = False
        self.archive_id.unlink()
        self.generated = False

    def export(self) -> None:
        """Start export."""

        if not self.uuid4:
            self.uuid4 = uuid.uuid4()

        # Ensure legal revision security and prevent double export.
        self.moves().datev_export = self.id
        self.generated = True

    def write_protection(self, vals):
        for export in self:
            if 'message_main_attachment_id' in vals:
                continue
            if export.generated and 'generated' not in vals:
                raise exceptions.UserError(_(
                    'Generated exports can not be modified.'
                ))

    def write(self, vals):
        self.write_protection(vals)
        return super().write(vals)

    def unlink_protection(self):
        for export in self:
            if export.generated:
                raise exceptions.UserError(_(
                    'Generated exports can not be deleted.'
                ))

    def unlink(self):
        self.unlink_protection()
        return super().unlink()
