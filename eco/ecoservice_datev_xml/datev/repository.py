# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .level import Level


class Repository(core.XsdComplexType):
    def __new__(
        cls,
        level: Level,
    ) -> dict:
        return {
            'level': level,
        }
