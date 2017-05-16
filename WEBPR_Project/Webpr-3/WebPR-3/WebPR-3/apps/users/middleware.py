from django.shortcuts import redirect
from django.core.urlresolvers import resolve


class UsablePasswordMiddleware(object):
    """Middleware for redirecting user to set up password if he wasn't set it
    up yet. This is actual for users that were registered by account admins.
    After such user was created, he gets activation email, confirms his email
    address and logins immediatly. But he didn't set up password, and this
    middleware redirects him to set up password.
    """

    def process_request(self, request):
        """Checks that user is authenticated and has password. If not -
        redirects to set up password view.
        """
        if request.user.is_authenticated() and \
                not request.user.has_usable_password():
            match = resolve(request.path)
            if match.url_name != 'account_set_password':
                return redirect('account_set_password')
