# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    logo_height = fields.Integer(
        related="company_id.logo_height",
        readonly=False
    )
    report_footer_as_image = fields.Boolean(
        string='Footer as image',
        related="company_id.report_footer_as_image",
        readonly=False,
    )
    report_footer_image = fields.Binary(
        string='Footer image',
        related="company_id.report_footer_image",
        readonly=False
    )
