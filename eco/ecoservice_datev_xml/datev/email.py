# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re

from . import core


class EMail(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        return None if (
            not value
            or len(value) > 60
            or not re.match(r'[^@]+@([^@\.\s]+\.)+([^@\.\s]{2,})', value)
        ) else value

#
