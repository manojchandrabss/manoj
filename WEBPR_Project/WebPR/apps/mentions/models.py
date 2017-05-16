import isoweek

from itertools import repeat
from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.management import settings
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import ArrayField, JSONField

from localflavor.us.models import (
    USStateField, USZipCodeField, PhoneNumberField
)
from model_utils.models import StatusModel, TimeStampedModel
from model_utils import Choices

from apps.mentions.managers import MentionManager, RatingManager, ToDoManager
from apps.users.models import Account


class Category(models.Model):
    """A model for category of merchant.

    A model for merchant's categories (undustries). Each category has a non
    unical code (MCC - Merchant Category Code) and array of codes for
    similar categories (if these exist). Also a category has special option
    `reportable`: if true - it is `Yes`, if false - `No1.6041-3(c)`.

    Attributes:
      name (str): Name of industry.
      code (int): Merchant Category Code.
      codes (array): Range of MCC for similar categories.
      reportable (bool): Special option for MCC.

    """
    _REPORTABLE_CHOICES = ((True, 'Yes'), (False, 'No1.6041-3(c)'))

    name = models.CharField(max_length=255, null=True, db_index=True)
    code = models.CharField(max_length=16, null=True, verbose_name='MCC')
    codes = ArrayField(
        models.CharField(max_length=4, blank=True, null=True),
        blank=True, null=True
    )
    reportable = models.BooleanField(default=True, choices=_REPORTABLE_CHOICES)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ('name', 'code')

    def __str__(self):
        return self.name

    def rating(self, extra_filter=None):
        """Method for calculating category rating.

        Args:
          extra_filter (dict): Extra parameters for rating filtration.

        Returns:
          float: Aggreagated rating for this category.

        """
        extra_filter = extra_filter or {}
        extra_filter.update({'merchant__category': self})
        rating = Rating.objects.filter(**extra_filter).aggregate(
            models.Avg('rating'))
        return rating['rating__avg']


class Mention(StatusModel, TimeStampedModel):
    """The comment from a some social network.

    Each mention related to certain Merchant.

    Attributes:
      merchant (object): An instance of ``Merchant`` model.
      mention_date (datetime): A date of mention.
      mention_link (str): An URL to mention surce.
      mention_text (str): Text of the mention.
      mention_type (str): A type, like ``review``, ``article``, etc.
      mention_author (str): The mention`s author.
      sentiment (str): ``positive``, ``negative``, ``neutral``.
      origin_site (str): An URL to site which contain the mention.
      is_relevant (bool): Is mention related to mercahnt?
      is_sentiment_fail (bool): Is sentiment analysis correct?
      sentiment_value (float): A float value from Semantria.
      u_id (uuid): An Universally Unique Identifier, primary key.

    """
    NEGATIVE = 'negative'
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NOT_ANALYSED = 'Not analysed'
    NEW = 'New'
    RESOLVED = 'Resolved'
    OLD = 'Old'
    DUPLICATE = 'Dupliciate'
    ASSIGNED = 'Assigned'
    FLAGGED = 'Flagged'
    UNASSIGNED = 'Unassigned'
    FACEBOOK = 'www.facebook.com'
    YELP = 'www.yelp.com'
    GOOGLE = 'plus.google.com'
    BBB = 'www.bbb.org'
    RIP = 'www.ripoffreport.com'
    _POLARITY = (
        (NEGATIVE, 'negative'),
        (POSITIVE, 'positive'),
        (NEUTRAL, 'neutral')
    )
    SOURCES = OrderedDict({
        FACEBOOK: {
            'color': '#3b5998',
            'label': 'Facebook'
        },
        YELP: {
            'color': '#af0606',
            'label': 'Yelp'
        },
        GOOGLE: {
            'color': '#dc4e41',
            'label': 'Google+'
        },
        BBB: {
            'color': '#005a78',
            'label': 'BBB'
        },
        RIP: {
            'color': '#ec2028',
            'label': 'RIP'
        }
    })
    TARGET_SITES = [tuple(repeat(k, 2)) for k in SOURCES.keys()]
    STATUS = Choices(
        NOT_ANALYSED, NEW, RESOLVED,
        OLD, DUPLICATE, ASSIGNED, FLAGGED
    )

    merchant = models.ForeignKey(
        'Merchant',
        related_name='mentions',
        blank=True,
        null=True
    )
    mention_date = models.DateField(blank=True, null=True)
    mention_link = models.CharField(max_length=255, blank=True, null=True)
    mention_text = models.TextField(null=True)
    mention_type = models.CharField(max_length=15, blank=True, null=True)
    mention_author = models.CharField(max_length=255, blank=True, null=True)
    sentiment = models.CharField(
        choices=_POLARITY, max_length=10, blank=True, null=True
    )
    origin_site = models.CharField(
        choices=TARGET_SITES, max_length=32, blank=True, null=True
    )
    is_relevant = models.BooleanField(default=True)
    is_sentiment_fail = models.BooleanField(default=False)
    sentiment_value = models.FloatField(blank=True, null=True)
    u_id = models.UUIDField(primary_key=True)
    text_hash = models.CharField(max_length=255, null=True, blank=True)

    objects = MentionManager()

    @property
    def closed_todo_count(self):
        """How many to-do closed for this mention.

        Returns (int):
          Count of closed to-do.

        """
        return self.todo.filter(is_closed=True).count()

    @property
    def overall_todo(self):
        """How many to-do for this mention overall.

        Returns (int):
          Count of to-do.

        """
        return self.todo.all().count()

    class Meta:
        ordering = ('-created',)
        unique_together = ('merchant', 'text_hash')
        index_together = ('merchant', 'status')

    def __str__(self):
        return str(self.u_id)


class Merchant(models.Model):
    """Base model of ``Merchant``.

    Merchant itself - company information, which is main object of
    investigation. This table contain all required information to persist
    merchant and create serch query for him.

    Attributes:
        official_name (str): A business name.
        short_name (array): An array for short name.
        keywords (str): Keywords for search.
        exclude_words  (str): Exclude words for relevance improvement.
        category (object): A ``Category`` instance.
        web_page (array): An array of URL`s.
        address (str): An adress of headquarter.
        city (str): A city.
        state (str): A state of US.
        zip_code (str): A ZIP code.
        phone (array): Phone numbers.
        product (array): Names of products which could identify a merchant.
        start_date (datetime): A date which we start search from
        dda (str): A some number to identify client.
        chargeback_total (int): A count of chargebacks.
        chargeback_prevented (int): A count of prevented chargebacks
        last_search_date (datetime): A date of last search.
        mentions_found (int): A count of merchant.
        ceo (str): A CEO name.
        email (str): A business email.

    """
    SOURCES_LIST = [source for source in Mention.SOURCES.keys()]

    official_name = models.CharField(
        max_length=255, unique=True, db_index=True
    )
    short_name = ArrayField(
        models.CharField(max_length=255, blank=True, null=True),
        blank=True, null=True, size=3
    )
    keywords = models.CharField(max_length=255, blank=True, null=True)
    exclude_words = models.CharField(
        max_length=255, blank=True, null=True, help_text='Comma-separated'
    )
    category = models.ForeignKey(
        Category, related_name='merchants', blank=True, null=True,
        db_index=True
    )
    web_page = ArrayField(
        models.URLField(blank=True, null=True),
        blank=True, null=True
    )
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zip_code = USZipCodeField(blank=True, null=True)
    phone = ArrayField(
        PhoneNumberField(blank=True, null=True),
        blank=True, null=True, size=3
    )
    product = ArrayField(
        models.CharField(max_length=255, blank=True, null=True),
        blank=True, null=True
    )
    start_date = models.DateTimeField(default=timezone.now)
    dda = models.CharField(max_length=255, null=True, blank=True)
    chargeback_total = models.IntegerField(blank=True, null=True)
    chargeback_prevented = models.IntegerField(blank=True, null=True)
    last_search_date = models.DateTimeField(blank=True, null=True)
    mentions_found = models.IntegerField(default=0)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    ceo = ArrayField(
        models.CharField(max_length=255, blank=True, null=True),
        blank=True, null=True
    )
    email = models.EmailField(max_length=254, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    search_settings = JSONField(blank=True, null=True, help_text='JSON')
    sources = ArrayField(
        models.CharField(max_length=32, blank=True),
        blank=True, null=True, default=SOURCES_LIST,
        help_text='Enable or disable sources for search.'
    )

    @property
    def get_open_todo_count(self):
        return self.mentions.prefetch_related('todo').filter(
            todo__is_closed=False).count()

    def get_mentions(self, date, period):
        """Function to find time slice of mentions for this merchant.

        Args:
          date (datetime): date.
          period (str): 'week' or 'month'.

        Returns:
          mentions (queryset): mentions for given merchants in given period.

        """
        PERIOD_MONTH = 'month'
        PERIOD_WEEK = 'week'
        excluding_statuses = [Mention.NOT_ANALYSED, Mention.FLAGGED]
        period = period.lower() if period else None
        qs = Q(origin_site__in=self.sources)

        if period == PERIOD_WEEK:
            w = isoweek.Week(
                year=date.isocalendar()[0],
                week=date.isocalendar()[1]
            )
            qs = qs & Q(created__gte=w.monday(), created__lte=w.sunday())
        elif period == PERIOD_MONTH:
            qs = qs & Q(created__month=date.month, created__year=date.year)

        return self.mentions.filter(qs).exclude(status__in=excluding_statuses)

    def get_absolute_url(self):
        return reverse('mentions:merchant', args=(self.pk,))

    class Meta:
        verbose_name = 'Merchant'
        verbose_name_plural = 'Merchants'
        ordering = ('official_name',)

    def __str__(self):
        return self.official_name


class ToDo(TimeStampedModel):
    """
    Table to manage tickets: linked with mention, status, user.
    Ticket or to-do is a some deal to do with mentions. When it is created,
    we can assign it to some user, add a comment, due date and priority.
    User can close ticket.
    Attributes:
        mention (Mention): FK to mention
        user (AppUser): FK to user, user who assigned for todo
        completed (datetime): date of finish of todo
        is_closed (bool): if True, then todo marks as closed
        comment (str): some comment for humans
        priority (str): some mark for todo importance
        due_date (datetime): deadline for todo to be closed
    """
    HIGH = 0
    MIDDLE = 1
    LOW = 2

    _PRIORITY = ((HIGH, 'High'), (MIDDLE, 'Middle'), (LOW, 'Low'))

    mention = models.ForeignKey(Mention, related_name='todo', blank=True,
                                null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                             null=True)
    completed = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    is_closed = models.BooleanField(default=False, db_index=True)
    priority = models.SmallIntegerField(choices=_PRIORITY,
                                        blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)

    objects = ToDoManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.comment)

    @property
    def due_date_retrospective(self):
        """
        Check if to-do due date is set to past or from past
        to define overdue to-do and prevent creaton to-do with date from past
        Returns:
            True if due date from past
            False if due date is ok
        """
        if self.due_date < timezone.now():
            return True
        else:
            return False


class Rating(TimeStampedModel):
    """
    Table to persist components for Merchant rating
    This table was made to avoid rating calculations "on the fly".
    Rating calculates week by week, so week, year and merchant
    should be unique tuple.
    Attributes:
        merchant (Merchant): FK to merchant
        week (int): number of week in year
        month (int): number of month in year
        year  (int): number of year
        rating (float): rating
        mentions_count (float): count of merchant
        pos_mentions (int): count of positive merchant
        neg_mentions (int): count of negative merchant
        solved_complaints (int): count of closed tickets
        unresolved_complaints (int): count of open tickets
    """

    merchant = models.ForeignKey(Merchant, related_name='ratings')
    year = models.IntegerField()
    week = models.IntegerField(blank=True, null=True)
    month = models.PositiveSmallIntegerField(blank=True, null=True)
    rating = models.FloatField(default=0)
    mentions_count = models.IntegerField(default=0)
    pos_mentions = models.IntegerField(default=0)
    neg_mentions = models.IntegerField(default=0)
    solved_todo = models.IntegerField(default=0)
    open_todo = models.IntegerField(default=0)

    objects = RatingManager()

    class Meta:
        # unique_together = (('merchant', 'week', 'month', 'year'),)
        index_together = (('merchant', 'week', 'month', 'year'),)


class Tracker(models.Model):
    """Table for custom trackers of Merchant.

    The table storing data for displaying trackers with custom mentions filter.

    Attributes:
      account (Account): FK for account.
      merchant (Merchant): FK for merchant.
      social_networks (array of str): A list of social networks.
      search_terms (str): Description of search terms.

    """
    SOCIAL_CHOICES = [(i[0], i[1].get('label')) for
                      i in Mention.SOURCES.items()]

    account = models.ForeignKey(Account, related_name='trackers')
    merchant = models.ForeignKey(Merchant, related_name='trackers')
    social_networks = ArrayField(models.CharField(max_length=255, blank=True,
                                                  null=True),
                                 blank=True, null=True)
    search_terms = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Tracker'
        verbose_name_plural = 'Trackers'


class TemporaryResults(TimeStampedModel):
    """
    Table to persist temporary results of google search
    and semantria analyze reports
    Attributes:
        merchant (Merchant): FK for merchant
        google_responce (str): response from google
        semantria_responce (str): responce from semantria
    """
    merchant = models.ForeignKey(Merchant, related_name='temp_results',
                                 blank=True, null=True)
    google_responce = models.TextField(blank=True, null=True)
    semantria_responce = models.TextField(blank=True, null=True)
