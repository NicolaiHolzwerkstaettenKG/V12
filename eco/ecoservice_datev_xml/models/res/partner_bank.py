from odoo import models

from ...datev import IBAN, Account, BankCode, BankName, SwiftCode


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def datev_bank_name(self) -> BankName:
        if not self.bank_id:
            return None
        name = self.bank_id.name
        name = name[0:30] if len(name) > 30 else name
        return BankName(name)

    def datev_bank_code(self) -> BankCode:
        if not self.bank_id:
            return None
        return BankCode(self.bank_id.bic)

    def datev_swift_code(self) -> SwiftCode:
        if not self.bank_id:
            return None
        return SwiftCode(self.bank_id.bic)

    def datev_iban(self) -> IBAN:
        return IBAN(self.sanitized_acc_number)

    def datev_account(self) -> Account:
        bank_name = self.datev_bank_name()
        iban = self.datev_iban()

        if (iban and not bank_name):
            return None  # 17321

        return Account(
            bank_name=bank_name,
            # bank_account=self.sanitized_acc_number,
            # bank_code=self.datev_bank_code(),
            swiftcode=self.datev_swift_code(),
            bank_country=(
                self.bank_id.country.datev_country_code()
                if self.bank_id else
                None
            ),
            iban=iban,
        )
