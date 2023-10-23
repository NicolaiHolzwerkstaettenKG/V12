# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, description, exception
from .country_code import CountryCode


class Address(core.XsdComplexType):
    def __new__(
        cls,
        name: description.Description50,
        zip: str,  # noqa: A002
        city: description.Description30,
        street: description.Description40 = None,
        boxno: str = None,
        country: CountryCode = None,
        phone: str = None,
        fax: str = None,
        email: str = None,
        gln: str = None,
        party_id: str = None,
    ) -> dict:
        """
        Address class.

        Args:
            name (Description50): Company/Person name, max. 50 characters
            zip (str): Post code, including international post codes
            city (Description30): _description_
            street (Description40, optional): House number and street
            boxno (str, optional): Box number
            country (CountryCode, optional): International country designation
            phone (str, optional): Telephone number
            fax (str, optional): Fax number
            email (str, optional): Email address
            gln (str, optional): Global Location Number
            party_id (str, optional): Original systems customer number
        """
        result = {
            '@name': name,
            '@zip': zip,
            '@city': city,
            '@street': street,
            '@boxno': boxno,
            '@country': country,
            '@phone': phone,
            '@fax': fax,
            '@email': email,
            '@gln': gln,
            '@party_id': party_id,
        }
        Address.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        Address.validate_name(data)
        Address.validate_city(data)
        Address.validate_zip(data)

    @staticmethod
    def validate_name(data):
        val = data.get('@name')
        if len(val) > 50:
            raise exception.DatevXmlLengthError(
                message='Company/Person name cannot exceed 50 characters.',
                value=val,
                range='0-50',
            )

    @staticmethod
    def validate_gln(data):
        val = data.get('@gln')
        if val and len(val) != 13:
            raise exception.DatevXmlLengthError(
                message='Global Location Number must consist of 13 digits.',
                value=val,
                range='13',
            )

    @staticmethod
    def validate_zip(data: dict):
        val = data.get('@zip')
        ref = data.get('@name')
        if not val:
            raise exception.DatevXmlMissingError(
                field=f'Address.zip ref: "{ref}"',
            )

    @staticmethod
    def validate_city(data: dict):
        val = data.get('@city')
        ref = data.get('@name')
        if not val:
            raise exception.DatevXmlMissingError(
                field=f'Address.city ref: "{ref}"',
            )
