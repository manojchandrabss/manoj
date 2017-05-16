from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Custom login required mixin for using with CBV.

    Differs from original with handling `next` parameter. Original
    `LoginRequiredMixin` adds GET parameter `next` to redirect user to
    previous page after login. But we use `apps.users.adapter.AccountAdapter`
    which custom handles redirect after login logic.

    Here we just set `redirect_field_name` to None so no GET parameter set and
    redirecting logic is fully inside `apps.users.adapter.AccountAdapter`

    """
    redirect_field_name = None


class AccessRequiredMixin(CustomLoginRequiredMixin):
    """Access to Merchant required mixin.

    The mixin allows access to merchant page only for superuser and
    merchant`s account users.

    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        account = user.account
        account_merchants_ids = account.merchants.values_list('id', flat=True)

        if obj.id not in account_merchants_ids and not user.is_superuser:
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)
