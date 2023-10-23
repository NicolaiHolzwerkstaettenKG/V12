# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core


class ExtensionFile(core.XsdComplexType):

    def __new__(
        cls,
        name: str,
    ) -> dict:
        return {
            '@xsi:type': 'File',
            '@name': name,
        }
