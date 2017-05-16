from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from allauth.account import signals
from allauth.account.utils import send_email_confirmation, perform_login
from allauth.account.views import ConfirmEmailView, PasswordSetView
from allauth.account import app_settings as allauth_settings

from apps.mentions.views.mixins import CustomLoginRequiredMixin
from apps.users.forms import UserCreationForm
from libs.views.mixins import AjaxableResponseMixin

__all__ = ['UserUpdateView', 'CreateUserForMerchant', 'CustomConfirmEmailView',
           'CustomPasswordSetView']


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing user profile (currently not used)

    """
    fields = ['first_name', 'last_name']

    def get_success_url(self):
        return reverse('users:profile')

    def get_object(self):
        return self.request.user


class CreateUserForMerchant(LoginRequiredMixin, AjaxableResponseMixin,
                            FormView):
    """CreateView for creating new user for merchant.

    This view is working using AJAX, so it returns JSONResponses with
    processing status and form.

    Attrs:
      form_class (object): A Django's form object. The form uses in view.
      template_name (str): Template name. Does not use in the view but
                           required as and attr.
    """
    form_class = UserCreationForm
    template_name = ''

    def get_form_kwargs(self):
        """Pass `merchants` arg for UserCreationForm.

        Merchants depends on requested user (ISO can add user to any of it's
        merchants account, merchants can add users just to it's account.

        """
        form_kwargs = super().get_form_kwargs()
        form_kwargs['merchants'] = self.request.user.account.merchants
        return form_kwargs

    def form_valid(self, form):
        """Form valid action.

        Save the new user for the Merchant and send verification email.

        Args:
          form (object): A Django's form object.

        Returns:
          JSON response with HTTP 200. Contains: created merchant name,
          his category and code.

        """
        user = form.save(request=self.request)
        signals.user_signed_up.send(sender=user.__class__,
                                    request=self.request, user=user)
        send_email_confirmation(self.request, user, signup=True)
        data = {'name': user.get_full_name()}
        return JsonResponse(data)


class CustomConfirmEmailView(ConfirmEmailView):
    """View for confirming user's email address. Differs from allauth`s
    `ConfirmEmailView` with login method on confirmation. Default view
    logins user just if he confirms email within same session as for signing
    up. But in our case some users is registered by their's admins. So we
    change `.login_on_confirm()` method to always log in confirmed user.
    And we will not have problems with security as we redirect user to password
    change with middleware.
    See docstring for original method for more details.
    """

    def login_on_confirm(self, confirmation):
        """Logins user that confirmed email.

        Args:
            confirmation: `allauth.account.models.EmailConfirmation` instance
                with user associated with that confirmation
        """
        user = confirmation.email_address.user
        return perform_login(self.request,
                             user,
                             allauth_settings.EmailVerificationMethod.NONE,
                             # passed as callable, as this method
                             # depends on the authenticated state
                             redirect_url=self.get_redirect_url)


class CustomPasswordSetView(CustomLoginRequiredMixin, PasswordSetView):
    """Custom password set view to not redirect user to the same page after
    password change. Original view had following logic:
        Authorized user go to set password
        Set password
        He is been logged out and stays on the password set page
        But he is not logged, so he is redirected to login page with
            `?next=/password/set`
        After login he redirects to /password/set, but then redirects to
            /password/change
        And he stays on that page until mannually go to other location.

    This view uses `CustomLoginRequiredMixin` that drops `next` parameter
    from login page and after login user redirects to page that defined
    in account adapter
    """
