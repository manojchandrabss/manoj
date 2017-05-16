from rest_framework import serializers
from django.utils import timezone


class DateTimeFieldWithTZ(serializers.DateTimeField):

    def enforce_timezone(self, value):
        """
        If `self.default_timezone` is `None`, always return naive datetimes.
        If `self.default_timezone` is not `None`, return aware datetimes.
        """
        try:
            tz = timezone._active.value
            if (self.default_timezone is not None) \
                    and not timezone.is_aware(value):
                return timezone.make_aware(value, tz)
            return value
        except AttributeError:
            return super().enforce_timezone(value)

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super().to_representation(value)
