# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .document import Document


class Content(core.XsdComplexType):
    def __new__(
        cls,
        document: Document,
    ) -> dict:
        return {
            'document': document,
        }
