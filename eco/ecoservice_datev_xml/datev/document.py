# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from uuid import UUID

from . import core, exception
from .description import Description40, Description255


class Document(core.XsdComplexType):
    def __new__(
        cls,
        description: Description40,
        keywords: Description255,
        extension: any,
        # repository: '',
        type: int,  # noqa: A002
        processID: int = None,  # noqa: N803
        guid: UUID = None,
    ) -> dict:
        result = {
            'description': {'$': description},
        }
        if keywords:
            result.update({
                'keywords': {'$': keywords},
            })
        result.update({
            'extension': extension,
            # 'repository': repository,
            '@type': type,
            '@processID': processID,
            '@guid': guid,
        })
        Document.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        Document.validate_type(data)
        Document.validate_process(data)

    @staticmethod
    def validate_type(data: dict):
        val = data.get('@type')
        if not val:
            return

        if val not in [1, 2]:
            raise exception.DatevXmlInvalidError(
                field='Document.type',
                value=val
            )

    @staticmethod
    def validate_process(data: dict):
        val = data.get('@processID')
        if not val:
            return

        if val not in [1, 2]:
            raise exception.DatevXmlInvalidError(
                field='Document.processID',
                value=val
            )
