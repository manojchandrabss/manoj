from __future__ import absolute_import
from apps.mentions.models import Merchant, Rating
from dateutil.relativedelta import relativedelta
from datetime import datetime


def fake_rating(request):
    """
    Function to generate fake ratings for tester
    Args:
        request (HTTPRequest): Request
    Returns:
        True
    """
    cur = datetime.now()
    if request.GET.get('date'):
        cur = datetime.strptime(request.GET.get('date'), '%d %m %y')
    merchants = Merchant.objects.all()
    for merchant in merchants:
        for i in range(7):
            date_week = cur - relativedelta(weeks=i)
            date_month = cur - relativedelta(months=i)
            positive = 1
            negative = 0
            total = 1
            rating = 1
            r_month = Rating.objects.create(merchant=merchant,
                                            month=date_month.month,
                                            year=date_month.year)
            r_week = Rating.objects.create(merchant=merchant,
                                           week=date_week.isocalendar()[1],
                                           year=date_week.isocalendar()[0])
            r_week.rating = rating
            r_month.rating = rating
            r_week.mentions_count = total
            r_month.mentions_count = total
            r_week.pos_mentions = positive
            r_month.pos_mentions = positive
            r_week.neg_mentions = negative
            r_month.neg_mentions = negative
            r_week.save()
            r_month.save()
            # modify creation date
            r_week.created = date_week
            r_week.save()
            r_month.created = date_month
            r_month.save()
    return True
