# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

# Standard
from datetime import datetime, timedelta
# 3rd
from dateutil.relativedelta import relativedelta
# Odoo
from odoo import fields, models
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class AutoDatevExportConfig(models.Model):
    _name = 'auto.datev.export.config'
    _description = 'Auto Datev Export Config'
    _rec_name = 'partner_id'

    # region Fields

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
    )

    period = fields.Selection(
        selection=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        required=True,
    )

    email_to = fields.Char(
        string='Email To',
    )

    company_id = fields.Many2one('res.company', string='Company', required=True)

    # endregion

    # region Constraints

    _sql_constraints = [
        (
            'partner_period_unique',
            'unique (partner_id, period)',
            'A period could be defined only one time for same partner.',
        )
    ]

    # endregion

    def _get_last_run(self, period, company_id):
        param_name = f'auto_datev_export.last_run.{period}.{company_id}'
        last_run = self.env['ir.config_parameter'].sudo().get_param(param_name)
        if last_run:
            return datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')
        return None

    def _set_last_run(self, period, company_id):
        param_name = f'auto_datev_export.last_run.{period}.{company_id}'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.env['ir.config_parameter'].sudo().set_param(param_name, current_time)

    def auto_mail_send(self):
        companies = self.env['res.company'].search([])
        for company in companies:
            company_self = self.with_context(force_company=company.id)

            configs = self.env['auto.datev.export.config'].search(
                [('company_id', '=', company.id)]
            )
            if configs:
                company_self.auto_send_mail_daily(configs, company.id)
                company_self.auto_send_mail_weekly(configs, company.id)
                company_self.auto_send_mail_monthly(configs, company.id)

    def auto_send_mail_daily(self, configs, company_id):
        last_run = self._get_last_run('daily', company_id)
        if last_run and (datetime.now() - last_run) < timedelta(days=1):
            return  # Skip if the last run was less than 1 day ago

        if last_run:
            start_date = last_run.date()
        else:
            start_date = datetime.today().date()
        configs_daily = configs.filtered(lambda a: a.period == 'daily')
        if configs_daily:
            end_date = datetime.today().date()
            ecofi_list = self.generate_financial_report_csv(start_date, end_date)
            if ecofi_list:
                self.send_mail_to_partners(configs_daily, ecofi_list)
                self._set_last_run('daily', company_id)

    def auto_send_mail_weekly(self, configs, company_id):
        last_run = self._get_last_run('weekly', company_id)
        if last_run and (datetime.now() - last_run) < timedelta(weeks=1):
            return  # Skip if the last run was less than 1 week ago

        if last_run:
            start_date = last_run.date()
        else:
            start_date = (fields.Datetime.now() - timedelta(days=7)).date()
        configs_weekly = configs.filtered(lambda a: a.period == 'weekly')
        if configs_weekly:
            if datetime.today().strftime('%A') in ['Monday', 'Montag']:
                end_date = datetime.today().date()
                ecofi_list = self.generate_financial_report_csv(start_date, end_date)
                if ecofi_list:
                    self.send_mail_to_partners(configs_weekly, ecofi_list)
                    self._set_last_run('weekly', company_id)

    def auto_send_mail_monthly(self, configs, company_id):
        last_run = self._get_last_run('monthly', company_id)
        if last_run and (datetime.now() - last_run) < timedelta(days=30):
            return  # skip if the last run was less than 1 month ago

        if last_run:
            start_date = last_run.date()
        else:
            start_date = (fields.Datetime.now() + relativedelta(months=-1)).date()
        configs_monthly = configs.filtered(lambda a: a.period == 'monthly')
        if configs_monthly:
            if datetime.today().strftime('%d') == '01':
                end_date = datetime.today().date()
                ecofi_list = self.generate_financial_report_csv(start_date, end_date)
                if ecofi_list:
                    self.send_mail_to_partners(configs_monthly, ecofi_list)
                    self._set_last_run('monthly', company_id)

    def generate_financial_report_csv(self, start_date, end_date):
        ecofi_list = []
        current_start_date = start_date
        while current_start_date <= end_date:
            current_year = current_start_date.year
            current_end_date = min(
                end_date,
                datetime(current_year, 12, 31).date()
            )

            ecofi = self.env['ecofi'].search([
                ('date_from', '=', start_date),
                ('date_to', '=', end_date),
            ])

            if ecofi:
                ecofi_list.append(ecofi)
            else:
                try:
                    new_export = self.env['ecofi'].ecofi_buchungen(
                        self.env.company.journal_ids, current_start_date, current_end_date
                    )

                    if new_export:
                        ecofi_list.append(new_export)

                except UserError as e:
                    _logger.warning(
                        f"Keine Buchungen für den Zeitraum {current_start_date} bis {current_end_date}: {str(e)}"
                    )

            current_start_date = current_end_date + timedelta(days=1)
        return ecofi_list

    def send_mail_to_partners(self, configs, ecofi_list):
        template_id = self.env.ref('ecoservice_financeinterface_datev_auto_export.send_email_finance_report_summary').id
        for config in configs:
            email_to = config.email_to or config.partner_id.email
            if not email_to:
                _logger.warning(f"Skipping partner {config.partner_id.name} due to missing email.")
                continue

            template = self.env['mail.template'].browse(template_id)
            if template:
                attachment = self.env['ir.attachment']
                for ecofi in ecofi_list:
                    attachment += self.create_attachment(ecofi)

                    module_is_installed = self.env['ir.module.module'].search(
                        [
                            ('name', '=', 'ecoservice_financeinterface_datev_xml'),
                            ('state', '=', 'installed')
                        ]
                    )
                    if module_is_installed:
                        if ecofi.xml_export_file:
                            xml_attachment_file = self.env['ir.attachment'].sudo().create({
                                'name': ecofi.name + '.zip',
                                'datas': ecofi.xml_export_file,
                                'res_model': 'ecofi',
                                'type': 'binary',
                                'store_fname': ecofi.xml_export_file,
                            })
                            attachment += xml_attachment_file

                values = template.generate_email(
                    config.id,
                    ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'attachment_ids']
                )
                values.update({
                    'subject': (
                        f"Financial Summary Report From {ecofi_list[0].date_from.strftime('%d-%m-%Y')} "
                        f"To {ecofi_list[-1].date_to.strftime('%d-%m-%Y')}"
                    ),
                    'email_from': self.env.user.email,
                    'email_to': email_to,
                    'attachment_ids': [(6, 0, attachment.ids)],
                    'body_html': template.body_html,
                })

                mail = self.env['mail.mail'].sudo().create(values)
                if mail:
                    mail.send()

    def create_attachment(self, ecofi):
        return self.env['ir.attachment'].sudo().create({
            'name': ecofi.name + '.csv',
            'datas': ecofi.csv_file,
            'res_model': 'ecofi',
            'type': 'binary',
            'store_fname': ecofi.csv_file,
        })
