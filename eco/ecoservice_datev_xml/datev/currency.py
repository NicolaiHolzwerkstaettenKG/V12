# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception


class Currency(core.XsdSimpleType):
    """Set a currency code based on ISO-4217."""

    def __new__(
        cls,
        value: str,
    ) -> str:
        cls.validate_length(value)
        cls.validate_value(value)
        return value

    @staticmethod
    def validate_length(value):
        if len(value) != 3:
            raise exception.DatevXmlLengthError(
                message='ISO-4217 currency codes must consist of 3 letters.',
                value=value,
                range=3
            )

    @staticmethod
    def valid_values():
        return [
            'AED', 'AFA', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'AON', 'AOR',
            'ARS', 'ATS', 'AUD', 'AWG', 'AZM', 'AZN', 'BAM', 'BBD', 'BDT',
            'BEF', 'BGL', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL',
            'BSD', 'BTN', 'BWP', 'BYB', 'BYN', 'BYR', 'BZD', 'CAD', 'CDF',
            'CHF', 'CLP', 'CMG', 'CNH', 'CNY', 'COP', 'CRC', 'CSD', 'CUP',
            'CVE', 'CYP', 'CZK', 'DEM', 'DJF', 'DJV', 'DKK', 'DOP', 'DZD',
            'ECS', 'EEK', 'EGP', 'ERN', 'ESP', 'ETB', 'EUR', 'FIM', 'FJD',
            'FKP', 'FRF', 'GBP', 'GEL', 'GHC', 'GHS', 'GIP', 'GMD', 'GNF',
            'GRD', 'GTQ', 'GWP', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF',
            'IDR', 'IEP', 'ILS', 'INR', 'IQD', 'IRR', 'ISK', 'ITL', 'JMD',
            'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD',
            'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LTL', 'LUF',
            'LVL', 'LYD', 'MAD', 'MDL', 'MGA', 'MGF', 'MKD', 'MMK', 'MNT',
            'MOP', 'MRO', 'MRU', 'MTL', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR',
            'MZM', 'MZN', 'NAD', 'NGN', 'NIO', 'NLG', 'NOK', 'NPR', 'NZD',
            'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PLZ', 'PTE',
            'PYG', 'QAR', 'ROL', 'RON', 'RSD', 'RUB', 'RUR', 'RWF', 'SAR',
            'SBD', 'SCR', 'SDD', 'SDG', 'SEK', 'SGD', 'SHP', 'SIT', 'SKK',
            'SLL', 'SOS', 'SRD', 'SRG', 'SSP', 'STD', 'SVC', 'SYP', 'SZL',
            'THB', 'TJR', 'TJS', 'TMM', 'TMT', 'TND', 'TOP', 'TRL', 'TRY',
            'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VEB',
            'VEF', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XCD', 'XEU', 'XOF',
            'XPF', 'YER', 'YUM', 'ZAR', 'ZMK', 'ZMW', 'ZRN', 'ZWD', 'ZWR',
        ]

    @staticmethod
    def validate_value(value):
        if value not in Currency.valid_values():
            raise exception.DatevXmlInvalidError(
                field='Currency.value',
                value=value,
            )
