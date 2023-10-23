# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core
from .client_name import ClientName
from .client_number import ClientNumber
from .consultant_number import ConsultantNumber
from .date import Date
from .description import Description255


class Header(core.XsdComplexType):
    def __new__(
        cls,
        date: Date,
        description: Description255 = None,
        consultantNumber: ConsultantNumber = None,  # noqa: N803
        clientNumber: ClientNumber = None,  # noqa: N803
        clientName: ClientName = None,  # noqa: N803
    ) -> dict:
        return {
            'date': {'$': date},
            'description': {'$': description},
            'consultantNumber': {'$': consultantNumber},
            'clientNumber': {'$': clientNumber},
            'clientName': {'$': clientName},
        }
