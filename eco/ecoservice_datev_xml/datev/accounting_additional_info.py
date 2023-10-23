# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception


class AccountingAdditionalInfo(core.XsdComplexType):
    def __new__(
        cls,
        type: str,  # noqa: A002
        content: str,
    ) -> dict:
        """
        Accountingadditionalinfo class.

        Args:
            type (str): Specifies the charakter.
            content (str): Specifies the content.
        """
        result = {
            '@type': type,
            '@content': content,
        }
        AccountingAdditionalInfo.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        AccountingAdditionalInfo.validate_type(data)
        AccountingAdditionalInfo.validate_content(data)

    @staticmethod
    def validate_type(data):
        info_type = data.get('@type')

        if not info_type:
            raise exception.DatevXmlMissingError(
                field='AccountingAdditionalInfo.type'
            )

    @staticmethod
    def validate_content(data):
        info_content = data.get('@content')

        if not info_content:
            raise exception.DatevXmlMissingError(
                field='AccountingAdditionalInfo.content'
            )
