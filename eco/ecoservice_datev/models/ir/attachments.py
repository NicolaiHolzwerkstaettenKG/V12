# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def datev_formats(self) -> list:
        return [
            '.bmp', '.csv', '.doc', '.docx', '.gif', '.jpg', '.jpeg', '.ods',
            '.odt', '.pdf', '.pkcs7', '.png', '.rtf', '.tif', '.tiff', '.xls',
            '.xlsx', '.xml'
        ]

    def datev_compatible(self):
        # https://apps.datev.de/help-center/documents/1007019
        return any(
            ext in self.display_name.lower()
            for ext in self.datev_formats()
        )
