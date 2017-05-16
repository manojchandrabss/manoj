import pytz
from django.utils import timezone


class TimezoneMiddleware(object):

    def process_request(self, request):
        try:
            tzname = request.META.get('HTTP_USER_TIMEZONE', None)
            if tzname:
                timezone.activate(pytz.timezone(tzname))
                request.timezone = pytz.timezone(tzname)
        except pytz.UnknownTimeZoneError:
            pass
