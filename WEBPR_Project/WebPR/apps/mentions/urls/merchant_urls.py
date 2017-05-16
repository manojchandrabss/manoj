from django.conf.urls import url

from apps.mentions.views import * # flake8: noqa


merchant_pattern = [
    # load merchant dashboard itself
    url(r'^merchant/(?P<pk>\d+)$', MerchantDetail.as_view(), name='merchant'),

    # add to-do for certain mention
    url(r'^merchant/addtodo$', AddToDoView.as_view(), name='addtodo'),

    # add merchant in iso interface
    url(r'^merchant/new$', AddMerchantView.as_view(), name='add_merchant'),

    # load mentions sub-page
    url(r'^merchant/(?P<pk>\d+)/mentions$', FilteredMentions.as_view(),
        name='mention_list'),

    url(r'^merchant/(?P<pk>\d+)/mentions/reset$', ResetMentionsView.as_view(),
        name='reset_mentions'),

    url(r'^merchant/(?P<merchant_id>\d+)/mentions/(?P<mention_u_id>[-\w]+)$',
        MentionFlagToggle.as_view(), name='mention_flag_toggle'),

    # load to-do sub-page
    url(r'^merchant/(?P<pk>\d+)/todos$', FilteredToDo.as_view(),
        name='todo_list'),

    url(r'^merchant/(?P<pk>\d+)/update$', MerchantUpdateView.as_view(),
        name='mention_update_view'),

    # close or re-open to-do
    url(r'^todo/(?P<pk>\d+)/toggle_status$', UpdateToDo.as_view(),
        name='update_todo'),
]
