import twilio
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from .utils import calculate_age


def validate_phone_number(value):
    """
    Using twilio lookup service validates phone number
    https://www.twilio.com/docs/api/rest/lookups
    :param value:
        number
    :return:
        raise exception if number is not valid
    """
    regex_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                     message="Invalid phone number")
    regex_validator(value)
    try:
        lookup = settings.TWILIO_LOOKUPS.phone_numbers.get(
            value, include_carrier_info=True)
    except twilio.rest.exceptions.TwilioRestException:
        raise ValidationError("Invalid phone number!")

    if lookup.carrier['type'] != 'mobile':
        raise ValidationError("Not a mobile phone number!")


def less_than_18(value):
    if calculate_age(value) < 18:
        raise ValidationError("You're too young to use this application!")
