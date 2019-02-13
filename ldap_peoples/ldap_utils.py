import time

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


def parse_time(timestr, tformat):
    time_struct = time.strptime(timestr, tformat)
    timestamp = time.mktime(time_struct)
    value = timezone.datetime.fromtimestamp(timestamp)
    utc = timezone.make_aware(value, timezone.pytz.utc)
    return utc.astimezone(timezone.get_default_timezone())


def parse_generalized_time(timestr):
    return parse_time(timestr, settings.LDAP_DATETIME_FORMAT)


def parse_pwdfailure_time(timestr):
    return parse_time(timestr,
                      settings.LDAP_DATETIME_MILLISECONDS_FORMAT)


def format_generalized_time(dt):
    """
    from datetime to zulu timestamp like 20180708095609Z
    """
    return dt.strftime(settings.LDAP_DATETIME_FORMAT)


def get_expiration_date():
  return datetime.now() + timedelta(days=settings.SHAC_EXPIRY_DURATION_DAYS)
