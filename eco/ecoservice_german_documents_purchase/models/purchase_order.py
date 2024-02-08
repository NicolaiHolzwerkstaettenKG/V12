# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'eco_report.mixin']

    # region Fields
    purchase_rfq = fields.Html(
        string='Request for Quotation (Top)',
    )
    purchase_confirmation = fields.Html(
        string='Purchase Order (Top)',
    )
    purchase_rfq_bottom = fields.Html(
        string='Request for Quotation (Bottom)',
    )
    purchase_confirmation_bottom = fields.Html(
        string='Purchase Order (Bottom)',
    )
    # endregion

    # region Compute Methods
    def _compute_dates(self):
        for rec in self:
            rec.report_compute_date = fields.Date.context_today(
                rec,
                fields.Datetime.from_string(rec.date_order or '')
            )
    # endregion

    # region Onchange Methods
    @api.onchange('partner_id')
    def get_template_text(self):
        # While changing partner: change the text according to partner's language
        # and do not reset this if text is written manually

        if self.partner_id:
            field_xml_list = []
            if (
                not self.purchase_rfq
                or self.purchase_rfq == '<p><br></p>'
            ):
                field_xml_list.append((
                    'purchase_rfq',
                    'ecoservice_german_documents_purchase.purchase_rfq_text',
                ))

            if (
                not self.purchase_rfq_bottom
                or self.purchase_rfq_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'purchase_rfq_bottom',
                    'ecoservice_german_documents_purchase.purchase_rfq_text_bottom',
                ))

            if (
                not self.purchase_confirmation
                or self.purchase_confirmation == '<p><br></p>'
            ):
                field_xml_list.append((
                    'purchase_confirmation',
                    'ecoservice_german_documents_purchase.purchase_order_text',
                ))

            if (
                not self.purchase_confirmation_bottom
                or self.purchase_confirmation_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'purchase_confirmation_bottom',
                    'ecoservice_german_documents_purchase.purchase_order_text_bottom',
                ))

            vals = self.env['text.template.config'].get_template_text(
                self.partner_id.lang,
                field_xml_list,
            )
            self.update(vals)
    # endregion

    # region CRUD Methods
    @api.model_create_multi
    def create(self, vals_list):
        fields_name = ['purchase_rfq', 'purchase_confirmation']
        rfq_vals_list = []

        for value in vals_list:
            values = self.is_html_field_empty(
                vals=value,
                fields=fields_name
            )
            rfq_vals_list.append(values)

        rfqs = super(PurchaseOrder, self).create(rfq_vals_list)

        for rfq in rfqs:
            rfq.get_template_text()

        return rfqs

    def write(self, values):
        fields_name = ['purchase_rfq', 'purchase_confirmation']
        values = self.is_html_field_empty(
            vals=values,
            fields=fields_name
        )
        return super(PurchaseOrder, self).write(values)
    # endregion

    # region Business Methods
    def _get_prefixes(self):
        quot = any(r.state in ['draft', 'sent', 'to approve'] for r in self)
        oc = any(r.state in ['purchase', 'done'] for r in self)
        return [x for x in [quot and _('RfQ'), oc and _('PO')] if x]
    # endregion

    @api.model
    def check_if_remove_html_tags(self, html_field):

        if hasattr(self.env['res.company'], 'remove_html_tags'):
            raw_text = self.env['res.company'].remove_html_tags(html_field)
        else:
            raw_text = html_field

        return raw_text
