# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .property import Property


class ExtensionInvoice(core.XsdComplexType):
    def __new__(
        cls,
        datafile: str,
        property: Property,  # noqa: A002
    ) -> dict:
        return {
            '@xsi:type': 'Invoice',
            '@datafile': datafile,
            'property': property,
        }
