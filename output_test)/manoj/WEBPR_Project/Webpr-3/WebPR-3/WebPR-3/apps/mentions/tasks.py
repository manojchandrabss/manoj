from __future__ import absolute_import

import isoweek
import logging
import traceback
import json
import re

from collections import namedtuple
from datetime import datetime, timedelta
from dateutil import rrule
from contextlib import suppress

from django.utils.timezone import now
from django.db import IntegrityError, reset_queries, models
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from allauth.account import signals
from allauth.account.utils import send_email_confirmation
from djcelery.models import TaskState
from celery import shared_task, states

from apps.mentions.models import (Merchant, Mention, Rating, Account,
                                  TemporaryResults)
from apps.mentions.utils.analyzer import Analyzer
from config.settings.common.business_logic import HIGH_THRESHOLD, LOW_THRESHOLD

logger = logging.getLogger(__name__)


def get_runned_tasks():
    """Get list of runned tasks.

    Returns:
      list: List of dictionaries with merchant ids {'merchant_id': 1}.

    """
    tasks = []
    current_tasks = TaskState.objects.filter(
        state__in=(states.RECEIVED, states.STARTED),
        kwargs__isnull=False
    )

    for task in current_tasks:
        kw = json.loads(re.sub('\'', '"', task.kwargs))

        with suppress(AttributeError):
            tasks.append(
                {'merchant_id': int(kw.get('merchant_id', 0))}
            )

    return tasks


def calculate_rating(merchant, date):
    """Calculate rating for merchant.

    Simple rating method if count of mentions less then LOW_THRESHOLD we
    should apply coefficient k = 0.33, if count of mentions between
    LOW_THRESHOLD and HIGH_THRESHOLD k = 0.66 and if count more then
    HIGH_THRESHOLD k = 1.

    Args:
      merchant (object): Merchant instance.
      date (datetime): date to calculate rating.

    Returns:
      float: Value of the rating.

    """
    excluding_statuses = [Mention.NOT_ANALYSED, Mention.FLAGGED]
    mentions = Mention.objects.filter(
        merchant=merchant,
        created__date__lte=date,
        origin_site__in=merchant.sources
    ).exclude(
        status__in=excluding_statuses
    )
    negative = mentions.filter(sentiment=Mention.NEGATIVE).count()
    total = mentions.count()

    if 0 <= total < LOW_THRESHOLD:
        k = 0.33
    elif LOW_THRESHOLD <= total < HIGH_THRESHOLD:
        k = 0.66
    else:
        k = 1

    if total > 0:
        rating = 100 * (1 - negative / total) * k
    else:
        rating = 0

    return rating


def calculate_mentions_count(merchant, date, period):
    """Update count of mentions inside the period of analysis.

    Args:
      merchant (Merchant): merchant instance.
      date (datetime.datetime): date to calculate rating.
      period (str): `week` or `month`.

    Returns:
      namedtuple: A named tuple that contains total count of mentions,
        count of posotive mentions and count of negative mentions.

    """
    mentions_in_period = merchant.get_mentions(date, period)
    mentions_count = len(mentions_in_period)
    pos_mentions = mentions_in_period.filter(
        sentiment=Mention.POSITIVE).count()
    neg_mentions = mentions_in_period.filter(
        sentiment=Mention.NEGATIVE).count()
    MentionsCount = namedtuple('MentionsCount', ('mentions_count',
                                                 'pos_mentions',
                                                 'neg_mentions'))

    return MentionsCount(
        mentions_count=mentions_count,
        pos_mentions=pos_mentions,
        neg_mentions=neg_mentions
    )


def update_rating(rating, merchant, date, period):
    """Function to update certain rating record in DB.

    Args:
      rating (object): Rating model instance.
      merchant (object): Merchant model instance.
      date (datetime): date to calculate rating
      period (str): `week` or `month`.

    """
    rating.rating = calculate_rating(merchant, date)
    mentions_count = calculate_mentions_count(merchant, date, period)
    rating.mentions_count = mentions_count.mentions_count
    rating.pos_mentions = mentions_count.pos_mentions
    rating.neg_mentions = mentions_count.neg_mentions
    rating.created = date
    rating.save()


@shared_task
def set_rating(*, merchant_id):
    """Task to calculate rating for merchant.

    Rating is calculating by following formula: R = (1-neg/total)*100*k

    neg - number of negative mentions
    total - total number of mentions
    k - coefficient

    if 0 < total < 30:
        k = 0.33
    elif 30 < total < 60:
        k = 0.66
    else k = 1

    Args:
      merchant_id (int): id of Merchant to calculated rating for.

    Returns:
        string: Name of the merchant.

    """
    merchant = Merchant.objects.get(id=merchant_id)
    date_list = []

    first_mention = Mention.objects.filter(
        merchant_id=merchant_id
    ).order_by('created').first()

    if first_mention:
        date_list = list(
            rrule.rrule(rrule.DAILY, until=now().date(),
                        dtstart=first_mention.created.date()))

    for date in date_list:
        try:
            # calculate rating for month
            r_month, _ = Rating.objects.get_or_create(
                merchant=merchant,
                month=date.month,
                year=date.year
            )
            update_rating(r_month, merchant, date, 'month')
            # calculate rating for week
            r_week, _ = Rating.objects.get_or_create(
                merchant=merchant,
                week=date.isocalendar()[1],
                year=date.isocalendar()[0]
            )
            update_rating(r_week, merchant, date, 'week')
        except Exception as e:
            logger.error(e)

    reset_queries()
    return merchant.official_name


@shared_task
def analyze_mentions(analyzer, *, merchant_id):
    """Task to analyze mentions by semantria and update it in db.

    Args:
      analyzer (Analyzer): instance of Analyzer class.

    Returns:
      int: count of updated mentions.

    """
    sent = 0
    updated = 0
    merchant = Merchant.objects.get(id=merchant_id)

    try:
        mentions_to_analyse = Mention.objects.filter(
            merchant=merchant,
            status=Mention.NOT_ANALYSED
        ).exclude(
            mention_text=''
        )

        if mentions_to_analyse:
            sent = len(mentions_to_analyse)

        res = analyzer.analyze(mentions_to_analyse)
        updated = Mention.objects.update_mentions(res)

        set_rating(merchant_id=merchant.id)
        reset_queries()
    except:
        logger.error('Something went wrong with analyser, {0}'.format(
            traceback.format_exc()), exc_info=True)

    return 'Sended {0}, updated in DB {1}'.format(sent, updated)


@shared_task
def get_query(*, merchant_id):
    """Get search results and save to database.

    Task for retrieving results from google and save results to db.

    Args:
      merchant_id (int): ID of merchant to get mentions.

    Returns:
      int: Count of mentions which have been updated after search.

    """
    updated = 0

    try:
        merchant = Merchant.objects.get(id=merchant_id)
        account = merchant.account_set.filter(type=Account.ISO).first()
        mentions_to_analyse = []

        if not account:
            account = Account.objects.all().first()

        analyzer = Analyzer(account.id, merchant)

        mentions_to_analyse = analyzer.crawl()

        if mentions_to_analyse:
            updated += len(mentions_to_analyse)

        Mention.objects.create_mentions(merchant, mentions_to_analyse)

        analyze_mentions.delay(analyzer, merchant_id=merchant_id)

        reset_queries()
    except:
        logger.error('Something went wrong with crawler, {0}'.format(
            traceback.format_exc()), exc_info=True)

    return updated


@shared_task
def clear_temporary_table():
    """
    Task to clear temporary table when lifetime - 33 days - exceeded.
    It will be called once at month.
    """
    time_threshold = now() - timedelta(days=33)
    TemporaryResults.objects.filter(created__lt=time_threshold).delete()


@shared_task
def recalculate_rating(*, merchant_id=None):
    """Task to recalculate rating for existing mentions.

    Args:
      merchant_id (int): Merchant ID if exists, default is None.

    Returns (int):
      Count of re-calculations.

    """
    i = 0

    if merchant_id:
        merchants = Merchant.objects.filter(pk=merchant_id)
    else:
        merchants = Merchant.objects.all()

    for merchant in merchants:
        mentions = Mention.objects.filter(
            merchant=merchant
        ).aggregate(
            models.Min('created')
        )
        min_date = mentions['created__min']
        date_list = list()

        try:
            date_list = list(
                rrule.rrule(rrule.DAILY, until=now().date(),
                            dtstart=min_date.date()))
        except Exception as e:
            print(e, mentions)

        for date in date_list:
            try:
                # calculate rating for month
                r_month, _ = Rating.objects.get_or_create(
                    merchant=merchant,
                    month=date.month,
                    year=date.year
                )
                update_rating(r_month, merchant, date, 'month')
                # calculate rating for week
                r_week, _ = Rating.objects.get_or_create(
                    merchant=merchant,
                    week=date.isocalendar()[1],
                    year=date.isocalendar()[0]
                )
                update_rating(r_week, merchant, date, 'week')
                i += 1
            except Exception as e:
                logger.error(e)

        reset_queries()
    return i


@shared_task
def check_rating_date():
    """
    Task to sort rating creation date
    Returns:
        rerecalculated (int): how mush ratings have been recalculated
    """
    recalculated = 0
    ratings = Rating.objects.all()
    for rating in ratings:
        week = rating.week
        month = rating.month
        year = rating.year
        date = rating.created
        if week:
            w = isoweek.Week(year=year, week=week)
            date = w.monday()
        if month:
            date = datetime(year=year, month=month, day=1)
        rating.created = date
        rating.save()
        recalculated += 1
    return recalculated


@shared_task
def bulk_merchant_import(merchants, users, request):
    """Task to bulk creation merchants and users.

    Args:
      users (list): list of AppUsers to create
      merchants (list): list of Merchants to create

    Returns:
      saved_merchants (int): count of saved merchants
      saved_users (int) count of saved users

    """
    saved_merchants, saved_users = 0, 0
    for merchant in merchants:
        try:
            merchant.save()
            account = merchant.account_set.filter(
                type=Account.MERCHANT).first()
            if users:
                user = users.pop(0)
                user.account = account
                user.save()
                signals.user_signed_up.send(sender=user.__class__,
                                            request=request, user=user)
                send_email_confirmation(request, user, signup=True)
                saved_users += 1
            saved_merchants += 1
        except IntegrityError:
            continue
        except ObjectDoesNotExist:
            continue

    MerchantsAndUsers = namedtuple(
        'MerchantsAndUsers', ('saved_merchants', 'saved_users')
    )

    try:
        send_mail(
            'Bulk import cumpleted',
            ('Merchants: {0} imported; '
             'Users: {1} imported').format(saved_merchants, saved_users),
            'no-reply@webpr.com',
            [request.user.email]
        )
    except:
        pass

    return MerchantsAndUsers(
        saved_merchants=saved_merchants,
        saved_users=saved_users
    )
