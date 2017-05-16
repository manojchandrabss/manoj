import isoweek
import logging
import hashlib

from calendar import monthrange
from collections import namedtuple
from datetime import timedelta
from itertools import chain

from django.db import models
from django.db import IntegrityError
from django.db.models import Q, ObjectDoesNotExist
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

PERIOD_MONTH = 'month'
PERIOD_WEEK = 'week'
STATUS_FLAGGED = 'Flagged'


class MentionManager(models.Manager):
    """Mention's model manager.

    Manager to persist mentions into DB and retrieve new mentions for
    sentiment analysis.

    We have such kind:
      1. Crawling
      2. Save a mentions to DB
      3. Get a mention from DB
      4. Sentiment analysis of mention
      5. Update mention in DB

    """

    def __init__(self):
        """Constructor for Mention Manager.

        Attributes:
          result_set (list): mentions to be persisted or updated in DB.

        """
        self.result_set = list()
        super().__init__()

    def create_mentions(self, merchant, mentions):
        """Save mentions in DB after crawling.

        Function to save new mention in DB after crawling, before analysis.

        Args:
          merchant (object): Merchant instance to create mentions.
          mentions (dict): mentions that have been received from search.

        """
        if mentions:
            for mention in mentions:
                try:
                    mention.created = mention.mention_date or timezone.now()
                    mention.merchant = merchant
                    mention.status = self.model.NOT_ANALYSED
                    h = hashlib.md5(mention.mention_text.encode())
                    mention.text_hash = h.hexdigest()
                    mention.save()
                except ValidationError:
                    logger.error('Data error!')
                except IntegrityError:
                    logger.warning('Mention already exists!')
                except TypeError:
                    logger.warning('Text is empty!')

    def update_mentions(self, sentiments):
        """Update mentions after sentiment analysis.

        Args:
          sentiment (dict): contains sentiment id, text and the
                            result of sentiment analysis.
        Returns:
          updated_count (int): count of mentions which have been updated.

        """
        updated_count = 0

        if sentiments:
            try:
                for sentiment in sentiments:
                    db_mention = self.get(pk=sentiment.get('u_id'))
                    db_mention.sentiment = sentiment.get('sentiment')
                    db_mention.status = self.model.NEW
                    db_mention.sentiment_value = sentiment.get(
                        'sentiment_value')
                    db_mention.save()
                    updated_count += 1
            except TypeError:
                logger.warning('Text is empty!')
            except ObjectDoesNotExist:
                logger.error('We lost this mention')
            except Exception as e:
                logger.error('Something went wrong with {0}'.format(e))
        return updated_count

    def get_mentions_for_period(self, merchants, date, period):
        """Get Mentions QS for merchants and period.

        Manager to get mentions for set of merchants according to certain
        period of week or month.

        Args:
          merchants (queryset): Merchant's QuerySet.
          date (datetime): date.
          period (str): 'week' or 'month'.

        Returns:
          mentions (queryset): mentions for given merchants in given period.

        """
        qs = Q(merchant__id__in=merchants.values_list('id', flat=True))
        excluding_statuses = [self.model.NOT_ANALYSED, self.model.FLAGGED]

        if period.lower() == 'week':
            w = isoweek.Week(year=date.isocalendar()[0],
                             week=date.isocalendar()[1])
            qs = qs & Q(created__gte=w.monday(), created__lte=w.sunday())
        else:
            qs = qs & Q(created__month=date.month, created__year=date.year)

        return self.filter(qs).exclude(status__in=excluding_statuses)


class RatingManager(models.Manager):
    """Manager for Rating model.

    Provides methods for get ratings, get reatings for period and get
    count of mentions.

    """

    def get_rating(self, merchants, date, period=PERIOD_WEEK):
        """Method to find rating for certain merchant.

        Args:
          merchant (Merchant): merchant to find rating for.
          date (datetime): date to define week.
          period (str): week or month.

        Returns:
          ratings (queryset): rating mathing query

        """
        qs = Q(merchant_id__in=merchants.values_list('id', flat=True))

        if period == 'PERIOD_MONTH':
            qs = qs & Q(month=date.month, year=date.year)
        else:
            qs = qs & Q(week=date.isocalendar()[1], year=date.isocalendar()[0])

        return self.filter(qs)

    def get_mention_counts(self, merchants, year, week=None, month=None):
        """Method to get count of mentions.

        Gets count for positive, negative and neutral mentions according
        to certain period.

        Args:
          merchants (list): list of Merchants.
          year (int): year.
          week (int): week.
          month (int): month.

        Returns:
          negative (int): number of negative mentions.
          positive (int): number of positive mentions.
          neutral (int): number of neutral mentions.

        """
        negative = 0
        positive = 0
        neutral = 0
        qs = Q(merchant_id__in=merchants.values_list('id', flat=True))

        if week:
            qs = qs & Q(year=year, week=week)
        else:
            qs = qs & Q(year=year, month=month)

        ratings = self.filter(qs)

        for rating in ratings:
            if rating.neg_mentions:
                negative += rating.neg_mentions
            if rating.pos_mentions:
                positive += rating.pos_mentions
            if rating.mentions_count:
                neutral += (rating.mentions_count -
                            rating.pos_mentions -
                            rating.neg_mentions)

        mention_counts = namedtuple('mention_counts', ('negative',
                                    'positive', 'neutral'))
        return mention_counts(negative=negative, positive=positive,
                              neutral=neutral)

    def get_rating_for_period(self, merchants, date, period):
        """Function to return rating by week or by month.

        Args:
          merchant (object): Merchant to find rating for.
          date (datetime): date.
          period (str): period - week or month.

        Returns (queryset): Ratings QuerySet.

        """
        merchants_ids = merchants.values_list('id', flat=True)

        if period == 'month':
            rating = self.filter(
                merchant_id__in=merchants_ids,
                month=date.month,
                year=date.year
            )

            if not rating:
                date = date - timedelta(days=7)
                rating = self.filter(
                    merchant_id__in=merchants_ids,
                    month=date.month,
                    year=date.year
                )
        else:
            rating = self.filter(
                merchant_id__in=merchants_ids,
                week=date.isocalendar()[1],
                year=date.isocalendar()[0]
            )

            if not rating:
                date = date - timedelta(days=7)
                rating = self.filter(
                    merchant_id__in=merchants_ids,
                    week=date.isocalendar()[1],
                    year=date.isocalendar()[0]
                )
        return rating


class ToDoManager(models.Manager):
    """ToDop manager.

    Calculate to-do count.

    """

    def get_todo_count(self, merchants, date, period=PERIOD_MONTH):
        """Method to calculate to-do count.

        Args:
          merchant (object): merchant to calculate to-do for.
          date (datetime): date to find period for to-do calculations.

        Returns:
          total (int): to-do overall.
          solved (int): solved to-do.

        """
        if period == PERIOD_WEEK:
            week = isoweek.Week(date.year, date.isocalendar()[1])
            first = week.monday()
            last = week.sunday()
        else:
            first = timezone.datetime(date.year, date.month, day=1)
            last = timezone.datetime(date.year, date.month,
                                     monthrange(date.year, date.month)[1])

        merchants_values = merchants.values_list('id', 'sources')
        merchants_ids = [i[0] for i in merchants_values]
        merchants_sources = set(chain.from_iterable(
            [i[1] for i in merchants_values]
        ))
        todo_set = self.filter(
            mention__merchant_id__in=merchants_ids,
            mention__origin_site__in=merchants_sources,
            created__gte=first,
            created__lte=last,
        ).exclude(
            mention__status=STATUS_FLAGGED
        )
        total = todo_set.count()
        solved = todo_set.filter(is_closed=True).count()
        todo_count = namedtuple('todo_count', ('total', 'solved'))

        return todo_count(total=total, solved=solved)
