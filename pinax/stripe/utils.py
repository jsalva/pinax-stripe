import datetime
import decimal

from django.utils import timezone

from .conf import settings


def convert_tstamp(response, field_name=None):
    try:
        utc_datetime = None
        if field_name and response[field_name]:
            utc_datetime = datetime.datetime.fromtimestamp(
                response[field_name],
                timezone.utc
            )
        if response is not None and not field_name:
            utc_datetime = datetime.datetime.fromtimestamp(
                response,
                timezone.utc
            )
        # convert to the right TIME_ZONE before stripping tzinfo
        if utc_datetime and not settings.USE_TZ:
            local_datetime = timezone.localtime(utc_datetime)
            return local_datetime.replace(tzinfo=None)
        return utc_datetime
    except KeyError:
        pass
    return None


# currencies those amount=1 means 100 cents
# https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
ZERO_DECIMAL_CURRENCIES = [
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw",
    "mga", "pyg", "rwf", "vuv", "xaf", "xof", "xpf",
]


def convert_amount_for_db(amount, currency="usd"):
    if currency is None:  # @@@ not sure if this is right; find out what we should do when API returns null for currency
        currency = "usd"
    return (amount / decimal.Decimal("100")) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else decimal.Decimal(amount)


def convert_amount_for_api(amount, currency="usd"):
    if currency is None:
        currency = "usd"
    return int(amount * 100) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else int(amount)
