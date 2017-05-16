from django.conf.urls import url

from apps.mentions.utils.service_scripts import calculate_rating


service_pattern = [
    # start rating calculation for merchant
    url(r'^merchant/(?P<pk>\d+)/rating$', calculate_rating),
    # start rating calculation for all merchants
    url(r'^rating$', calculate_rating)
]
