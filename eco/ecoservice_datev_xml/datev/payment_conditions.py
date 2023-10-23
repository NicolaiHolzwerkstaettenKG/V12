# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core, exception
from .amount import Amount
from .currency import Currency
from .date import Date


class PaymentConditions(core.XsdComplexType):

    def __new__(
        cls,
        payment_conditions_text: str,
        due_date: Date = None,
        time_of_payment: Date = None,
        amount_of_payment: Amount = None,
        time_of_part_payment: Date = None,
        amount_of_part_payment: Amount = None,
        payment_conditions_id: str = None,
        payment_dunning_block: str = None,
        currency: Currency = None,
        bonus: list = None,
        discount: list = None,
        rebate: list = None,
    ) -> dict:
        """
        Paymentconditions class.

        Args:
            payment_conditions_text (str): Payment conditions text
            due_date (Date, optional): Invoice due date
            time_of_payment (Date, optional): Amount of payment
            amount_of_payment (Amount, optional): _description_. Defaults to None.
            time_of_part_payment (Date, optional): Date of partial payment
            amount_of_part_payment (Amount, optional): Amount of partial payment
            payment_conditions_id (str, optional): id of the payment-condition
            payment_dunning_block (str, optional): ?
            currency (Currency, optional):  Currency for the amounts.
            bonus (list, optional): List of Bonus type
            discount (list, optional): List of Discount type
            rebate (list, optional): List of Rebate type
        """
        result = {
            '@payment_conditions_text': payment_conditions_text,
            '@due_date': due_date,
            '@time_of_payment': time_of_payment,
            '@amount_of_payment': amount_of_payment,
            '@time_of_part_payment': time_of_part_payment,
            '@amount_of_part_payment': amount_of_part_payment,
            '@payment_conditions_id': payment_conditions_id,
            '@payment_dunning_block': payment_dunning_block,
            '@currency': currency,
            'bonus': bonus,
            'discount': discount,
            'rebate': rebate,
        }
        PaymentConditions.validate(result)
        return result

    @staticmethod
    def validate(data) -> None:
        PaymentConditions.validate_payment_conditions_text(data)

    @staticmethod
    def validate_payment_conditions_text(data):
        value = data.get('@payment_conditions_text')
        if not value:
            raise exception.DatevXmlMissingError(
                'PaymentConditions.payment_conditions_text'
            )
