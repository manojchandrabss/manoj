from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from config.settings.common.static import MEDIA_ROOT, MEDIA_URL
from apps.users.views import CustomConfirmEmailView, CustomPasswordSetView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('apps.mentions.urls', namespace='mentions')),
    url(r'^accounts/', include('allauth.urls')),
    url(r"^password/set/$", CustomPasswordSetView.as_view(),
        name="account_set_password"),
    url(r"^users/confirm-email/(?P<key>\w+)/$",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email"),
    url(r'^users/', include('apps.users.urls', namespace='users')),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
