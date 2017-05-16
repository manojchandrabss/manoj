from django.conf.urls import url

from apps.mentions.views.statistics import *  # flake8: noqa


statistics_pattern = [
    # url for statistics page
    url(r'^statistics$', StatisticsView.as_view(), name='statistics'),
    url(r'^statistics/by_source$', ComplaintsBySource.as_view(),
        name='by_source'),
    url(r'^statistics/by_time$', ComplaintsOverTime.as_view(),
        name='by_source'),
]
