import uuid

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.timezone import now
from django.views.generic import CreateView, DetailView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView

from apps.mentions.forms.forms import AddToDoModelForm, MerchantModelForm
from apps.mentions.models import Mention, Merchant, Rating, ToDo
from apps.mentions.tasks import get_query, get_runned_tasks
from apps.mentions.utils.flynsarmy_paginator.flynsarmy_paginator import \
    FlynsarmyPaginator
from apps.mentions.views.filters import AssignedFilter, ResolvedFilter
from apps.mentions.views.mixins import (AccessRequiredMixin,
                                        CustomLoginRequiredMixin)
from apps.users.forms import UserCreationForm
from apps.users.models import Account, AppUser
from libs.views.mixins import AjaxableResponseMixin

__all__ = ['MerchantDetail', 'FilteredToDo', 'FilteredMentions', 'UpdateToDo',
           'AddToDoView', 'FakeMention', 'MerchantUpdateView',
           'MentionFlagToggle', 'ResetMentionsView']


class MerchantDetail(CustomLoginRequiredMixin, DetailView):
    """
    Merchant dashboard. Display general information concerned with merchant:
    company name, rating of the merchant and rating of the merchant industry
    """
    template_name = "merchant/analytics.html"
    context_object_name = 'company'

    def get_queryset(self):
        """Accessing to merchant detail has the following logic:
        if user is superuser - has access to all merchants
        else user has acess just to his account merchants

        Returns:
            QuerySet: merchants that user have access to
        """
        if self.request.user.is_superuser:
            return Merchant.objects.all()
        else:
            return self.request.user.account.merchants.all()

    def get_context_data(self, **kwargs):
        """Adds UserCreationForm to template context
        """
        context = super().get_context_data(**kwargs)
        context['user_add_form'] = UserCreationForm(
            merchants=self.request.user.account.merchants,
            initial={'merchant': self.object}
        )
        context['form'] = MerchantModelForm(instance=self.object)

        return context


class FilteredToDo(CustomLoginRequiredMixin, FilterView):
    """Show all ``Todo`` with filter and pagination.

    Show todo`s with applied filter and pagination.

    Attributes:
      adjacent_pages (int): A parameter for FlynsarmyPaginator.
      filterset_class (objectr): An instance of custom ``Filter``.

    """
    model = ToDo
    template_name = 'merchant/todo.html'
    paginator_class = FlynsarmyPaginator
    page_kwarg = 'todo'
    paginate_by = 10
    adjacent_pages = 2
    filterset_class = ResolvedFilter

    def get_merchant(self):
        """Get current merchant based on url parameter `pk`.

        Raises:
          PermissionDenied if user has no access to this merchant.

        """
        merchant = Merchant.objects.get(id=self.kwargs['pk'])

        if self.request.user.is_superuser:
            return merchant
        else:
            if merchant not in self.request.user.account.merchants.all():
                raise PermissionDenied
            return merchant

    def get_queryset(self):
        """Get all mentions for merchant.

        Returns:
          QuerySet: all ToDos for this merchant.

        """
        self.merchant = self.get_merchant()

        return ToDo.objects.filter(
            mention__merchant=self.merchant,
            mention__origin_site__in=self.merchant.sources
        ).exclude(
            mention__status__in=[Mention.FLAGGED]
        )

    def get_paginator(self, *args, **kwargs):
        """Adds kwarg `adjacent_pages` to `ListView.get_paginator`.

        Returns (object):
          An instance of the paginator for this view.

        """
        kwargs.update({'adjacent_pages': self.adjacent_pages})

        return super().get_paginator(*args, **kwargs)


class UpdateToDo(CustomLoginRequiredMixin, DetailView):
    """View for switching TODO status
    """

    def get_queryset(self):
        """Returns TODOs that related to user account
        """
        qs = Q()
        user = self.request.user

        if not user.is_superuser:
            merchants_ids = user.account.merchants.values_list('id', flat=True)
            qs = qs & Q(mention__merchant__id__in=merchants_ids)

        return ToDo.objects.filter(qs).exclude(mention__status=Mention.FLAGGED)

    def update_rating(self, todo):
        """
        Method to find rating for certain merchant
        Args:
            todo: to-do which we're going to open or close
        Returns:
            rating (Rating): rating object
        """
        date = todo.created
        mention = todo.mention
        rating = Rating.objects.get_or_create(
            merchant_id=mention.merchant_id,
            week=date.isocalendar()[1],
            year=date.isocalendar()[0]
        )
        created = rating[1]
        rating = rating[0]
        # if rating object created first time
        if created and todo.is_closed:
            # re-open to-do
            rating.solved_todo = 0
            rating.open_todo = 1
        elif created and not todo.is_closed:
            # close to-do
            rating.solved_todo = 1
            rating.open_todo = 0
        else:
            if todo.is_closed:
                # re-open to-do if rating already exists
                rating.solved_todo -= 1
                rating.open_todo += 1
            else:
                # close to-do if rating already exists
                rating.solved_todo += 1
                rating.open_todo -= 1
        rating.save()

    def get(self, request, *args, **kwargs):
        """Get requested ToDo and change it's status
        """
        todo = self.get_object()
        self.update_rating(todo)
        todo.is_closed = not todo.is_closed
        todo.save()
        return JsonResponse({'status': todo.is_closed}, status=200)


class FilteredMentions(CustomLoginRequiredMixin, FilterView):
    """Show filtered and paginated mentions list.

    Show mentions with applied filter and pagination.

    Attributes:
      adjacent_pages (int): A parameter for ``FlynsarmyPaginator``.
      filterset_class (objectr): An instance of custom ``Filter``.

    """
    template_name = 'merchant/mentions.html'
    paginator_class = FlynsarmyPaginator
    page_kwarg = 'page'
    paginate_by = 5
    adjacent_pages = 2
    filterset_class = AssignedFilter
    excluded_statuses = [Mention.NOT_ANALYSED]

    def get_merchant(self):
        """Get current merchant based on url parameter `pk`.

        Raises:
          PermissionDenied if user has no access to this merchant.

        """
        merchant = Merchant.objects.get(id=self.kwargs['pk'])

        if self.request.user.is_superuser:
            return merchant
        else:
            if merchant not in self.request.user.account.merchants.all():
                raise PermissionDenied
            return merchant

    def get_queryset(self):
        """Get all mentions for merchant.

        Returns:
          QuerySet: all ToDos for this merchant.

        """
        self.merchant = self.get_merchant()

        return Mention.objects.filter(
            merchant=self.merchant,
            origin_site__in=self.merchant.sources
        ).exclude(
            status__in=self.excluded_statuses
        )

    def get_paginator(self, *args, **kwargs):
        """Adds kwarg `adjacent_pages` to `ListView.get_paginator`.

        Returns (object):
          An instance of the paginator for this view.

        """
        kwargs.update({'adjacent_pages': self.adjacent_pages})

        return super().get_paginator(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = now()
        context['company'] = Merchant.objects.get(pk=self.kwargs.get('pk'))
        # Display in form only Account's users and who has already confirmed
        context['users'] = AppUser.objects.filter(
            account__in=self.merchant.account_set.all(),
            account__type=Account.MERCHANT, last_login__isnull=False)
        context['priority'] = ToDo._PRIORITY
        return context


class AddToDoView(CustomLoginRequiredMixin, AjaxableResponseMixin, CreateView):
    """
    Form to create new todo
    """
    model = ToDo
    form_class = AddToDoModelForm

    def get_success_url(self):
        """
        If add succeed, return to same page
        """
        pk = self.request.POST['company']
        return reverse_lazy('mentions:merchant', kwargs={'pk': pk})

    def set_rating(self, mention):
        """
        Method to find rating for certain merchant
        Args:
            todo: to-do which we're going to open or close
        Returns:
            rating (Rating): rating object
        """
        date = now()
        merchant = mention.merchant
        rating = Rating.objects.get_or_create(merchant=merchant,
                                              week=date.isocalendar()[1],
                                              year=date.isocalendar()[0])
        rating = rating[0]
        # if rating.open_todo:
        rating.open_todo += 1
        rating.save()

    def form_valid(self, form, **kwargs):
        """
        Action if form is valid
        Args:
            form: form
        """
        mention = Mention.objects.get(
            u_id=self.request.POST.get('mention_uid'))
        form.instance.mention = mention
        self.set_rating(mention)
        mention.status = Mention.STATUS['Assigned']
        mention.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Update the form kwargs (to AddToDoView.__init__)

        Update kwargs for providing custom users's queryset. Only account's
        users have access to add ToDo for the Mention.

        Returns:
          kwargs (dict): user_qs is a queryset for 'user' form field.

        """
        kwargs = super().get_form_kwargs()
        company_id = self.request.POST.get('company')
        merchant_id = company_id if str(company_id).isnumeric() else 0
        accounts_list = Account.objects.filter(merchants=merchant_id,
                                               type=Account.MERCHANT)
        user_qs = AppUser.objects.filter(account__in=accounts_list,
                                         last_login__isnull=False)
        kwargs.update({'user_qs': user_qs})
        return kwargs


class FakeMention(CustomLoginRequiredMixin, CreateView):
    """
    Special view to make a dummy mentions.
    Available by "/fake" only if DEBUG
    """
    model = Mention
    template_name = 'merchant/fake_mention.html'
    fields = ['merchant', 'mention_date', 'mention_link', 'mention_text',
              'status',
              'mention_type', 'mention_author', 'sentiment', 'origin_site',
              'is_relevant', 'is_sentiment_fail', 'sentiment_value', 'u_id']

    def get_success_url(self):
        """
        If add succeed, return to same merchant page
        """
        pk = self.request.POST['merchant']
        return reverse_lazy('mentions:merchant', kwargs={'pk': pk})

    def get_initial(self):
        """
        Get initial uuid for dummy mention
        Returns:
            u_id (uuid): pk for fake mention
        """
        return {'u_id': str(uuid.uuid4()).replace("-", "")}

    def form_valid(self, form):
        return super().form_valid(form)


class MerchantUpdateView(CustomLoginRequiredMixin, AjaxableResponseMixin,
                         UpdateView):
    """Form for update Merchant.

    The merchant is updating using ajax. Returns merchant ID.

    """
    model = Merchant
    form_class = MerchantModelForm

    def get_queryset(self):
        """Customize a get queryset method for access control to merchant.

        Returns:
          QuerySet: merchants that user have access to.

        """
        if self.request.user.is_superuser:
            return Merchant.objects.all()

        return self.request.user.account.merchants.all()

    def form_valid(self, form, **kwargs):
        return super().form_valid(form)


class MentionFlagToggle(CustomLoginRequiredMixin, View):
    """Toggle mention's Flagged status.

    If status is Flagged -- set Assigned (if mention does not have todos).

    """

    def get(self, request, merchant_id, mention_u_id):
        status = Mention.UNASSIGNED
        user = request.user
        qs = Q(u_id=mention_u_id, merchant_id=merchant_id)

        if not user.is_superuser:
            qs = qs & Q(merchant__account__id=user.account_id)

        try:
            mention = Mention.objects.get(qs)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Does not exist'}, status=400)

        if mention.status == Mention.FLAGGED:
            if mention.todo.count():
                status = Mention.ASSIGNED
        else:
            status = Mention.FLAGGED

        mention.status = status
        mention.save()

        return JsonResponse({'status': mention.status}, status=200)


class ResetMentionsView(AccessRequiredMixin, SingleObjectMixin, View):
    """Reset mentions for a selected merchant.

    Here is proceeding reset mentions and ratings for a selected merchant.
    After reset will be started new search and analysis.

    """
    model = Merchant

    def reset_mentions(self, merchant):
        merchant.mentions.all().delete()
        merchant.ratings.all().delete()
        merchant.temp_results.all().delete()

    def get(self, request, **kwargs):
        merchant = self.get_object()
        runned_tasks = get_runned_tasks()

        if merchant.id not in [t['merchant_id'] for t in runned_tasks]:
            self.reset_mentions(merchant)
            get_query.delay(merchant_id=merchant.id)

            message = ('Mentions have been removed. Search started.')
        else:
            message = ('The process is busy now. Please wait a while and try '
                       'again later.')

        messages.info(self.request, message)

        return HttpResponseRedirect(merchant.get_absolute_url())
