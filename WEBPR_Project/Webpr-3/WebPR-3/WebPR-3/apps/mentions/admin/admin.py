from django.contrib import admin, messages
from django.utils.text import Truncator

from django_object_actions import (DjangoObjectActions,
                                   takes_instance_or_queryset)

from apps.mentions.models import (Merchant, Mention, ToDo, Category, Tracker,
                                  Rating, TemporaryResults)
from apps.mentions.admin.filters import RatingsMonthWeekListFilter
from apps.mentions.tasks import get_query, get_runned_tasks

__all__ = ['MerchantAdmin', 'MentionAdmin', 'MentionAdmin', 'RatingAdmin',
           'TrackerAdmin']


@admin.register(Merchant)
class MerchantAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Admin interface for Merchant class.

    Set up custom fieldsets, actions and display in list.

    """
    actions = ['search_mentions']
    change_actions = ['search_mentions']
    list_display = ('official_name', 'category', 'start_date', 'sources',
                    'last_search_date')
    list_select_related = True
    search_fields = ['official_name']
    fieldsets = [
        ('General information', {'fields': ['official_name', 'short_name',
                                            'dda', 'web_page', 'product']}),
        ('Sources', {'fields': ['sources']}),
        ('Category', {'fields': ['category'], 'classes': []}),
        ('Contact information', {'fields': ['ceo', 'email', 'city', 'state',
                                            'address', 'zip_code', 'phone']}),
        ('Ext Address', {'fields': ['location']}),
        ('Query information', {
            'fields': ['keywords', 'exclude_words', 'search_settings']
        }),
        ('Date information: time before the date will be excluded from search',
         {'fields': ['start_date']}),
    ]

    @takes_instance_or_queryset
    def search_mentions(modeladmin, request, queryset):
        """Add custom action control for Merchant(s)

        Here is adding custom actions for the Merchant and Merchants list.
        Search mentions uses for manually starting mention's search for
        selected objects.

        Before search, there is a check for existing of already running tasks.

        """
        runned_tasks = get_runned_tasks()
        already_runned_ids = [t['merchant_id'] for t in runned_tasks]
        now_runned_ids = []

        for merchant in queryset.exclude(id__in=already_runned_ids):
            get_query.delay(merchant_id=merchant.id)
            now_runned_ids.append(merchant.id)

        messages.info(request, ('Search has been started for {0} '
                                'merchants.'.format(len(now_runned_ids))))
    search_mentions.label = 'Search mentions'
    search_mentions.short_description = ('Search mentions for selected '
                                         'Merchants')


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    """Admin class for Mentions, mainly for debug purposes
    """
    list_display = ('u_id', 'merchant', 'origin_site', '_mention_text',
                    'sentiment', 'status', 'created', 'modified')
    list_filter = ('merchant', 'origin_site', 'sentiment', 'status')
    date_hierarchy = 'modified'

    def _mention_text(self, obj):
        return Truncator(obj.mention_text).chars(50)

    _mention_text.short_description = 'Text'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin class for Ratings, mainly for debug purposes
    """
    list_display = ('merchant', 'week', 'month', 'year', 'rating',
                    'open_todo', 'solved_todo', 'mentions_count',
                    'pos_mentions', 'neg_mentions', 'created', 'modified')
    list_editable = ('week', 'month', 'year', 'rating',
                     'open_todo', 'solved_todo', 'mentions_count',
                     'pos_mentions', 'neg_mentions')
    readonly_fields = ('created',)
    list_filter = ('merchant', RatingsMonthWeekListFilter,)


@admin.register(ToDo)
class ToDoAdmin(admin.ModelAdmin):
    """Admin class for to-do, mainly for debug purposes
    """

    fields = ['comment', 'user', 'mention', 'is_closed']
    list_display = ('comment', 'is_closed', 'created',
                    '_mod_week')

    def _mod_week(self, obj):
        return obj.modified.isocalendar()[1]


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    """Admin class for Tracker

    Displays tracker's list with merchant name and social networks list.
    """
    list_display = ('merchant', 'social_networks')
    list_display_links = ('merchant',)
    list_select_related = True


class CategoryMerchantFilter(admin.SimpleListFilter):
    """
    Class to filter merchants according to its category
    """
    title = 'merchants'
    parameter_name = 'merchant'

    def lookups(self, request, model_admin):
        look_ups = list()
        for merchant in Merchant.objects.all():
            look_ups.extend((merchant.category, (merchant.official_name)))
        return look_ups

    def queryset(self, request, queryset):
        return queryset.filter(category=self.value())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin class for Category

    Displays categories list with name and MCC code.

    """

    def merchants(self, obj):
        """
        Method to show merchants for this category
        """
        return Merchant.objects.filter(category=obj)

    list_display = ('name', 'code', 'codes', 'reportable', 'merchants')
    list_filter = ('merchants',)
    list_select_related = True


@admin.register(TemporaryResults)
class TemporaryAdmin(admin.ModelAdmin):
    """
    Admin class for temporary results table
    """
    list_display = ('merchant', 'created')
    list_filter = ('merchant',)
