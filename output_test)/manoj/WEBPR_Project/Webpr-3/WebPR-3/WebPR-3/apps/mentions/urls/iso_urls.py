from django.conf.urls import url
from apps.mentions.views import *               # flake8: noqa

iso_pattern = [
    # complaints view for iso
    url(r'^complaints$', ComplaintsView.as_view(), name='complaints'),

    # url to show solved/usolved chart
    url(r'^solved$', SolvedTodoView.as_view(), name='solved'),

    # url to show big five
    url(r'^big_five$', BigFiveView.as_view(), name='big_five'),

    # url to show responce rate for iso
    url(r'^response_rate_iso$', SolvedTodoView.as_view(),
        name='response_rate_iso'),

    # url to get merchant responce rate
    url(r'^response_rate_merchant$', SolvedTodoView.as_view(),
        name='merchant_response'),

    # url to get industry complaints chart for iso dashboard
    url(r'^industry_complaints_chart$', IndustryComplaintsChartView.as_view(),
        name='industry_complaints_chart'),

    # url to get mentions chart for iso dashboard
    url(r'^iso_mention_chart$', MentionsChartView.as_view(),
        name='iso_mention_chart'),

    # url to get score for iso
    url(r'^score$', ScoreView.as_view(), name='score'),

    # table with lowest ranked merchants for ISO dashboard
    url(r'^lowest_ranked$', LowestRankedMerchantsView.as_view(),
        name='lowest_ranked'),

    # url for merchants bulk import
    url(r'^bulk_import$', BulkImportView.as_view(), name='bulk_import'),

    # url when merchant import confirmed
    url(r'^confirmed_import$', ConfirmedMerchantImportView.as_view(),
        name='confirmed_import'),

    # url for download sample .csv
    url(r'^download_sample$', download_sample, name='download_sample'),

    # web hook for semantria
    url(r'^hook/processed.json$', SemantriaHookView.as_view(),
        name='semantria_hook'),

    # iso dashboard itself
    url(r'^$', DashboardView.as_view(), name='dashboard'),
]
