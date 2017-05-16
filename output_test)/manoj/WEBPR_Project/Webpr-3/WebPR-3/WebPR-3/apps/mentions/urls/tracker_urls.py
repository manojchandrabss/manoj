from django.conf.urls import url
from apps.mentions.views import * # flake8: noqa

tracker_pattern = [
    url(r'^tracker$', TrackerList.as_view(), name='trackers'),
    url(r'^tracker/(?P<pk>\d+)/mentions$', TrackerMentionsListView.as_view(),
        name='tracker-mentions'),
    url(r'^tracker/create$', TrackerCreateView.as_view(),
        name='tracker-create'),
    url(r'^tracker/(?P<pk>\d+)/update$', TrackerUpdateView.as_view(),
        name='tracker-update'),
    url(r'^tracker/(?P<pk>\d+)/delete$', TrackerDeleteView.as_view(),
        name='tracker-delete'),
]
