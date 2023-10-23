# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models

from ...datev import (
    Address,
    Description30,
    Description40,
    Description50,
    EMail,
    InvoiceParticipant,
)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def datev_address(self) -> Address:
        if not self:
            return None

        return Address(
            name=Description50(self.name),
            zip=self.zip,
            city=Description30(self.city),
            street=Description40(self.street),
            country=self.country_id.datev_country_code(),
            email=EMail(self.email),
            phone=self.phone.replace(' ', '') if self.phone else None,
            fax=self.fax if hasattr(self, 'fax') else None,
            party_id=str(self.id),
        )

    def datev_accounts(self) -> list:
        result = []
        banks = self.bank_ids.filtered(
            lambda x: x.company_id.id in (False, self.env.company.id)
        )
        for bank in banks:
            bank_data = bank.datev_account()
            if not bank_data:
                continue
            result.append(bank_data)
        return result

    def datev_invoice_participant(self) -> InvoiceParticipant:
        return InvoiceParticipant(
            address=self.datev_address(),
            account=self.datev_accounts(),
        )
