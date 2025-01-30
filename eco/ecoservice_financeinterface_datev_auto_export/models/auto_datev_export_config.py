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

    export_backtrack = fields.Selection(
        selection=[
            ('last_export', 'Last Automatic Export'),
            ('start_of_year', 'Start of the Year'),
            ('last_export_minus_1', 'Last Export - 1 Month'),
            ('last_export_minus_2', 'Last Export - 2 Month'),
            ('last_export_minus_3', 'Last Export - 3 Month'),
            ('previous_year_start', 'Start of the Last Year'),
        ],
        string="Export Backtrack",
        default='last_export',
        required=True,
    )

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

    def _calculate_start_date(self, config, last_run, default_period):

        if config.export_backtrack == 'start_of_year':
            start_date = datetime(datetime.now().year, 1, 1).date()
        elif config.export_backtrack == 'previous_year_start':
            start_date = datetime(datetime.now().year - 1, 1, 1).date()
        elif config.export_backtrack.startswith('last_export_minus_'):
            months_offset = int(config.export_backtrack.split('_')[-1])
            start_date = (last_run + relativedelta(months=-months_offset)).date() if last_run else default_period
        elif config.export_backtrack == 'last_export':
            start_date = last_run.date() if last_run else default_period
        else:
            start_date = default_period

        if last_run:
            start_date = min(last_run.date(), default_period, start_date)
        else:
            start_date = min(default_period, start_date)

        return start_date

    def auto_mail_send(self):
        companies = self.env['res.company'].search([])
        for company in companies:
            company_self = self.with_company(company.id)

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

        configs_daily = configs.filtered(lambda a: a.period == 'daily')
        if configs_daily:
            for config in configs_daily:
                start_date = self._calculate_start_date(config, last_run, datetime.today().date())
                end_date = datetime.today().date()
                ecofi_list = self.generate_financial_report_csv(start_date, end_date)
                if ecofi_list:
                    self.send_mail_to_partners(config, ecofi_list)
                    self._set_last_run('daily', company_id)

    def auto_send_mail_weekly(self, configs, company_id):
        last_run = self._get_last_run('weekly', company_id)
        if last_run and (datetime.now() - last_run) < timedelta(weeks=1):
            return  # Skip if the last run was less than 1 week ago

        configs_weekly = configs.filtered(lambda a: a.period == 'weekly')
        if configs_weekly:
            for config in configs_weekly:
                start_date = self._calculate_start_date(
                    config, last_run, (fields.Datetime.now() - timedelta(days=7)).date()
                )
                if datetime.today().strftime('%A') in ['Monday', 'Montag']:
                    end_date = datetime.today().date()
                    ecofi_list = self.generate_financial_report_csv(start_date, end_date)
                    if ecofi_list:
                        self.send_mail_to_partners(config, ecofi_list)
                        self._set_last_run('weekly', company_id)

    def auto_send_mail_monthly(self, configs, company_id):
        last_run = self._get_last_run('monthly', company_id)
        if last_run and (datetime.now() - last_run) < timedelta(days=30):
            return  # skip if the last run was less than 1 month ago

        configs_monthly = configs.filtered(lambda a: a.period == 'monthly')
        if configs_monthly:
            for config in configs_monthly:
                start_date = self._calculate_start_date(
                    config, last_run, (fields.Datetime.now() + relativedelta(months=-1)).date()
                )
                if datetime.today().strftime('%d') == '01':
                    end_date = datetime.today().date()
                    ecofi_list = self.generate_financial_report_csv(start_date, end_date)
                    if ecofi_list:
                        self.send_mail_to_partners(config, ecofi_list)
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
                ('company_id', '=', self.env.company.id),
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
                for ecofi_item in ecofi_list:
                    if len(ecofi_item) > 1:
                        for ecofi in ecofi_item:
                            attachment |= self.create_attachment(ecofi)
                    else:
                        attachment |= self.create_attachment(ecofi_item)

                    module_is_installed = self.env['ir.module.module'].search(
                        [
                            ('name', '=', 'ecoservice_financeinterface_datev_xml'),
                            ('state', '=', 'installed')
                        ]
                    )
                    if module_is_installed:
                        if ecofi_item.xml_export_file:
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

                if ecofi_list:
                    date_from = min(ecofo.date_from for ecofi_item in ecofi_list for ecofo in ecofi_item)
                    date_to = max(ecofo.date_to for ecofi_item in ecofi_list for ecofo in ecofi_item)

                    values.update({
                        'subject': (
                            f"Financial Summary Report From {date_from.strftime('%d-%m-%Y')} "
                            f"To {date_to.strftime('%d-%m-%Y')}"
                        ),
                        'email_from': self.env.user.email,
                        'email_to': email_to,
                        'attachment_ids': [(6, 0, attachment.ids)],
                        'body_html': template.body_html,
                    })
                else:
                    _logger.error("eco-fi list is empty. Cannot generate email subject.")

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
