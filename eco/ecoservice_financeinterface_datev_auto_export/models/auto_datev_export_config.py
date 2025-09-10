# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from dateutil.relativedelta import relativedelta, MO
from odoo import _, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AutoDatevExportConfig(models.Model):
    _name = 'auto.datev.export.config'
    _description = 'Auto Datev Export Config'

    # region Fields

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Send to',
    )

    period = fields.Selection(
        selection=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        required=True,
    )

    to_export = fields.Selection(
        selection=[
            ('csv_export', 'CSV-Export'),
            ('belege_export', 'Belege Export'),
            ('csv_and_beleg_export', 'CSV+Beleg Export'),
        ],
    )

    fi_datev_xml_installed = fields.Boolean(
        compute='_compute_fi_datev_xml_installed'
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )

    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Journals',
    )

    # endregion

    # region Methods

    def _compute_fi_datev_xml_installed(self):
        module = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'ecoservice_financeinterface_datev_xml'),
            ('state', '=', 'installed'),
        ])
        if module:
            self.fi_datev_xml_installed = True
        else:
            self.fi_datev_xml_installed = False

    def create_export_send_mail(self, period):
        start_date, end_date = self.get_time_period(period)
        records = self.search([])
        for record in records:
            if record.period == period:
                '''Nice solution to catch the UserError and continue on other
                entries in this model. The sequencing is still messed up - but
                has nothing to do with this.'''
                try:
                    ecofi = record.create_export(start_date, end_date)
                    record._cr.commit()
                    attachments = record.get_attachments(ecofi)
                    record.send_mail(attachments, start_date, end_date)
                except UserError:
                    record._cr.rollback()

    def get_time_period(self, period):
        today = fields.Date.today()
        if period == 'daily':
            start_date = today - relativedelta(days=1)
            end_date = start_date
        elif period == 'weekly':
            start_date = today - relativedelta(weeks=1, weekday=MO(-1))
            end_date = start_date + relativedelta(days=6)
        elif period == 'monthly':
            last_month_start = today - relativedelta(months=1)
            last_month_start = last_month_start.replace(day=1)
            last_month_end = today.replace(day=1) - relativedelta(days=1)
            start_date = last_month_start
            end_date = last_month_end
        return start_date, end_date

    def create_export(self, start_date, end_date):
        journals = self.journal_ids if self.journal_ids else self.env.company.journal_ids
        if self.fi_datev_xml_installed and self.to_export:
            ecofi = self.env['ecofi'].ecofi_buchungen(
                journals, start_date, end_date, self.to_export
            )
        else:
            ecofi = self.env['ecofi'].ecofi_buchungen(
                journals, start_date, end_date
            )
        return ecofi

    def get_attachments(self, ecofi):
        attachments = []

        if ecofi.csv_file:
            csv_attachment = self.env['ir.attachment'].create({
                'name': ecofi.name + '.csv',
                'datas': ecofi.csv_file,
                'res_model': 'ecofi',
                'type': 'binary'
            })
            attachments.append(csv_attachment.id)

        if self.fi_datev_xml_installed:
            if ecofi.xml_export_attachment_id:
                xml_attachment = ecofi.xml_export_attachment_id
                attachments.append(xml_attachment.id)

        return attachments

    def send_mail(self, attachments, start_date, end_date):
        template = self.env.ref(
            'ecoservice_financeinterface_datev_auto_export.email_template_auto_datev_export'
        )
        if not template:
            _logger.error('Email template not found!')
            return False

        if not self.partner_id:
            _logger.warning('There is no email recipient!')

        template.attachment_ids = self.env['ir.attachment'].browse(attachments)
        template.subject = _('Datev Export from {start_date} to {end_date}').format(
            start_date=start_date.strftime('%d.%m.%Y'),
            end_date=end_date.strftime('%d.%m.%Y'),
        )
        template.send_mail(self.id)

        _logger.info('Email sent.')

    # endregion
