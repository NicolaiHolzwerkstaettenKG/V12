# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo.exceptions import UserError


class DatevXmlError(Exception):
    def __init__(self, message):
        raise UserError(
            message=f'- DATEV XML Validation Error -\n{message}'
        )
