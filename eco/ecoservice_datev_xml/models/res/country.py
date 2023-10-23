# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models

from ...datev import CountryCode


class ResCountry(models.Model):
    _inherit = 'res.country'

    def datev_country_code(self) -> CountryCode:
        if not self:
            return None

        return CountryCode(self.code)
