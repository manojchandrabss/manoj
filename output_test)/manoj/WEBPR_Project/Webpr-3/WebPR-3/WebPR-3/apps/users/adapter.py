from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.core.urlresolvers import reverse_lazy


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    SocialAccountAdapter used to link social accounts with existiong users
    # https://github.com/pennersr/django-allauth/issues/418#issuecomment-107880925
    """

    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook
        # accounts with mobile numbers only, but allauth takes care of this
        # case so just ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data['email'].lower()
            email_address = EmailAddress.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        user = email_address.user
        sociallogin.connect(request, user)


class AccountAdapter(DefaultAccountAdapter):
    """Account adapter class for django-allauth. Redefine
    `.get_login_redirect_url()` to redirect logged user to his dashboard
    """

    def get_login_redirect_url(self, request):
        """Rewrite logic for getting redirect URL after login.
        If it is regular user (that have connected account):
            if it is ISO user - redirect to ISO dashboard
            if it is Merchant user - redirect to merchant dashboard
        If user has no connected account - redirect to mentions page
        """
        if request.user.account:
            if request.user.is_iso:
                return reverse_lazy('mentions:dashboard')
            elif request.user.is_merchant:
                merch = request.user.account.merchants.first()
                return reverse_lazy('mentions:merchant', args=(merch.pk, ))
        return reverse_lazy('mentions:mentions')
