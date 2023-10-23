# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import api, fields, models


class EcoReportMixIn(models.AbstractModel):
    _name = 'eco_report.mixin'
    _description = 'Eco Report Mixin'

    # region Fields
    report_compute_date = fields.Date(
        compute='_compute_dates',
    )
    report_line_index = fields.Integer(
        default=1,
    )
    # endregion

    # region Compute Methods
    def _compute_dates(self):
        for rec in self:
            # Prevent CacheMiss Exception (#13000)
            rec.report_compute_date = False
    # endregion

    # region Business Methods
    def set_report_line_index(self, value):
        self.report_line_index = value

    def eco_report_prefix(self):
        return '_'.join(self._get_prefixes())

    def eco_report_suffix(self):
        return '_'.join(
            [
                x for x
                in self.mapped(self._get_name_field())
                if x and x != '/'
            ]
        )

    def eco_report_name(self):
        return '-'.join(
            x for x
            in [
                self.eco_report_prefix(),
                self.eco_report_suffix(),
            ]
            if x
        )

    @staticmethod
    def is_html_field_empty(vals, fields):
        blank = ['<p><br></p>', '<p>&nbsp;</p>']

        for field in fields:
            if vals.get(field) in blank:
                vals[field] = False

        return vals

    @api.model
    def _get_name_field(self):
        return 'name'

    def _get_prefixes(self):
        return []
    # endregion
