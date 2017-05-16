from django.contrib import admin


class RatingsMonthWeekListFilter(admin.SimpleListFilter):
    """List filter for filtering ratings by month ratings or week ratings
    """
    title = 'Month or week ratings'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('month', 'Month ratings'),
            ('week', 'Week ratings'),
        )

    def queryset(self, request, queryset):
        """Filters queryset basing on passed value
        """
        value = self.value()

        if value == 'month':
            return queryset.filter(week__isnull=True)

        elif value == 'week':
            return queryset.filter(month__isnull=True)

        return queryset
