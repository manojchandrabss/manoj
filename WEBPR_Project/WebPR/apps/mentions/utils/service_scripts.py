import random
import hashlib
import logging

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.db import IntegrityError

from apps.users.models import Account
from apps.mentions.utils.analyzer import Analyzer
from apps.mentions.tasks import (
    get_query, recalculate_rating, analyze_mentions, check_rating_date
)
from apps.mentions.models import Mention, Merchant

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

__all__ = ['start_search', 'calculate_rating', 'create_fake_rating',
           'check_creation_date_for_mentions', 'check_rating_creation_date',
           'analyze_all_mentions', 'generate_hash', ]


@user_passes_test(lambda u: u.is_superuser)
def start_search(request, pk=None):
    """
    Start search and analysis on-the-fly
    Args:
        pk (int): primary key of certain merchant
    Returns:
        redirect to the same page
    """
    if not pk:
        merchants = Merchant.objects.all()
        for merchant in merchants:
            get_query.delay(merchant.id, merchant_id=merchant.id)
        return redirect('/')
    else:
        get_query.delay(pk, merchant_id=pk)
        return redirect('/merchant/{0}'.format(pk))


@user_passes_test(lambda u: u.is_superuser)
def calculate_rating(request, pk=None):
    """
    function to direct call for rating calculation
    Args:
        request: request
        pk (int): id of merchant
    """
    if not pk:
        recalculate_rating.delay()
        return redirect('/')
    else:
        recalculate_rating.delay(merchant_id=pk)
        return redirect('/merchant/{0}'.format(pk))


@user_passes_test(lambda u: u.is_superuser)
def create_fake_rating(request):
    """
    Function for testing purposes
    Args:
        request:request
        pk (int): id of merchant
    """
    from apps.mentions.utils.tool_tester import fake_rating
    fake_rating(request)
    return redirect('/')


@user_passes_test(lambda u: u.is_superuser)
def check_creation_date_for_mentions(request):
    """
    Sort mentions by following rule:
        if there is a mention_date then created = mention_date
    Args:
        request: request
    """
    mentions = Mention.objects.all()
    for mention in mentions:
        if mention.mention_date:
            mention.created = mention.mention_date
            mention.save()
    return redirect('/')


@user_passes_test(lambda u: u.is_superuser)
def check_rating_creation_date(request):
    """
    Sort rating creation date
    Args:
        request: request
    """
    check_rating_date.delay()
    return redirect('/')


@user_passes_test(lambda u: u.is_superuser)
def analyze_all_mentions(request, pk=None):
    """
    Function to provide separate analyze for merchants on demand
    Args:
        request: request
    """
    merchants = Merchant.objects.all()

    if pk:
        merchants = merchants.filter(id=pk)

    for merchant in merchants:
        account = Account.objects.filter(merchants=merchant, type='i').first()
        if not account:
            account = Account.objects.all().first()
        analyzer = Analyzer(account.id, merchant)
        analyze_mentions.delay(analyzer, merchant.id)
    return redirect('/')


@user_passes_test(lambda u: u.is_superuser)
def randomize_mentions(request):
    """
    Function to create a lot of fake mentions
    Args:
        request:
    Returns:

    """
    for merchant in Merchant.objects.all():
        for n in random.randint(5, 50):
            s = random.randint(0, 2)
            sentiment = Mention.POLARITY[s][1]
            Mention.objects.create(merchant=merchant,
                                   sentiment=sentiment,
                                   status=Mention.STATUS)


@user_passes_test(lambda u: u.is_superuser)
def generate_hash(request):
    """
    Function to generate text hash for old mentions
    Args:
        request: request
    Returns:
    """
    mentions = Mention.objects.filter(text_hash__isnull=True)
    for mention in mentions:
        try:
            h = hashlib.md5(mention.mention_text.encode())
            mention.text_hash = h.hexdigest()
            mention.save()
        except IntegrityError:
            mention.delete()
    return redirect('/')


def generate_fake_sentiments(merchant_id, recalculate_ratings=False):
    """Generate fake sentiments for not analysed mentions.

    Args:
      merchant_id (int): Id of the merchant, that needs new sentiments.
      recalculate_ratings (bool): The merchant needs new ratings.

    """
    merchant = Merchant.objects.get(pk=merchant_id)
    choice = random.choice
    sentiments = [Mention.POSITIVE, Mention.NEGATIVE, Mention.NEUTRAL]
    updated = []

    for mention in merchant.mentions.filter(status=Mention.NOT_ANALYSED):
        mention.sentiment = choice(sentiments)
        mention.status = Mention.NEW
        mention.save()

        updated.append(mention)

    if recalculate_ratings:
        recalculate_rating(merchant_id=merchant_id)

    logger.info('Updated: %s mention(s)', len(updated))
