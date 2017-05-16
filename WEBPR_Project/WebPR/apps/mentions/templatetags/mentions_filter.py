from django import template

from apps.mentions.models import Mention

register = template.Library()


@register.simple_tag
def mentions_filter(tracker):
    """Geting mentions for the tracker

    The filter returns mentions for a selected tracker whose having same social
    sources (is origin site in social networks list?).

    Args:
      tracker (object): An Tracker model's object.

    Returns:
      QuerySet: A limited mention's QuerySet (latest 10 objects) that contains
      mentions which do not have status Not analysed.

    """
    qs = Mention.objects.filter(merchant_id=tracker.merchant_id,
                                origin_site__in=tracker.social_networks)
    return qs.exclude(status__in=[Mention.NOT_ANALYSED])[:30]
