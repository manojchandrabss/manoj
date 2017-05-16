from django.conf.urls import url
from .views import UserUpdateView, CreateUserForMerchant


urlpatterns = [
    url(r'^profile/$', UserUpdateView.as_view(), name='profile'),
    url(r'^create_user$', CreateUserForMerchant.as_view(),
        name="create_user"),
]
