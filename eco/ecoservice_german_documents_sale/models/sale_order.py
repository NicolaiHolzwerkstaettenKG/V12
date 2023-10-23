# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files at the root directory for full details.

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'eco_report.mixin']

    # region Fields
    sale_quotation = fields.Html(
        string='Sale Quotation (Top)',
    )
    sale_confirmation = fields.Html(
        string='Sale Confirmation (Top)',
    )
    proforma_invoice = fields.Html(
        string='Proforma Invoice (Top)',
    )
    sale_quotation_bottom = fields.Html(
        string='Sale Quotation (Bottom)',
    )
    sale_confirmation_bottom = fields.Html(
        string='Sale Confirmation (Bottom)',
    )
    proforma_invoice_bottom = fields.Html(
        string='Proforma Invoice (Bottom)',
    )
    # endregion

    # region Compute Methods
    def _compute_dates(self):
        for rec in self:
            rec.report_compute_date = fields.Date.context_today(
                rec,
                fields.Datetime.from_string(rec.date_order or ''),
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
                not self.sale_quotation
                or self.sale_quotation == '<p><br></p>'
            ):
                field_xml_list.append((
                    'sale_quotation',
                    'ecoservice_german_documents_sale.sale_quotation_text',
                ))

            if (
                not self.sale_quotation_bottom
                or self.sale_quotation_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'sale_quotation_bottom',
                    'ecoservice_german_documents_sale.sale_quotation_text_bottom',
                ))

            if (
                not self.sale_confirmation
                or self.sale_confirmation == '<p><br></p>'
            ):
                field_xml_list.append((
                    'sale_confirmation',
                    'ecoservice_german_documents_sale.sale_confirmation_text',
                ))

            if (
                not self.sale_confirmation_bottom
                or self.sale_confirmation_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'sale_confirmation_bottom',
                    'ecoservice_german_documents_sale.sale_confirmation_text_bottom',
                ))

            if (
                not self.proforma_invoice
                or self.proforma_invoice == '<p><br></p>'
            ):
                field_xml_list.append((
                    'proforma_invoice',
                    'ecoservice_german_documents_sale.proforma_invoice_text',
                ))

            if (
                not self.proforma_invoice_bottom
                or self.proforma_invoice_bottom == '<p><br></p>'
            ):
                field_xml_list.append((
                    'proforma_invoice_bottom',
                    'ecoservice_german_documents_sale.proforma_invoice_text_bottom',
                ))

            vals = self.env['text.template.config'].get_template_text(
                self.partner_id.lang,
                field_xml_list,
            )
            self.update(vals)
    # endregion

    # region CRUD Methods
    @api.model
    def create(self, values):
        fields_name = ['sale_quotation', 'sale_confirmation', 'proforma_invoice']
        values = self.is_html_field_empty(
            vals=values,
            fields=fields_name
        )
        return super(SaleOrder, self).create(values)

    def write(self, values):
        fields_name = ['sale_quotation', 'sale_confirmation', 'proforma_invoice']
        values = self.is_html_field_empty(
            vals=values,
            fields=fields_name
        )
        return super(SaleOrder, self).write(values)
    # endregion

    # region Business Methods
    def _get_prefixes(self):
        if self._is_pro_forma_report():
            return [_('Pro-Forma')]

        quot = any(r.state in ['draft', 'sent'] for r in self)
        oc = any(r.state in ['sale', 'done'] for r in self)

        return [
            x for x
            in [
                quot and _('Quotation'),
                oc and _('Order-Confirmation'),
            ]
            if x
        ]

    def _is_pro_forma_report(self):
        return self.env.context.get('report_xml_id') in [
            'sale.report_saleorder_pro_forma',
            'ecoservice_german_documents_sale.report_quotation_proforma_template',
            'ecoservice_german_documents_sale'
            '.report_quotation_proforma_template_without_logo',
        ]
    # endregion
