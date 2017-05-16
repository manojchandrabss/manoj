from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.http import JsonResponse

from apps.mentions.forms.forms import TrackerModelForm
from apps.mentions.models import Mention, Tracker
from apps.mentions.views.mixins import CustomLoginRequiredMixin
from libs.views.mixins import AjaxableResponseMixin

__all__ = ['TrackerList', 'TrackerCreateView', 'TrackerUpdateView',
           'TrackerDeleteView', 'TrackerMentionsListView']


class TrackerAjaxableResponseMixin(AjaxableResponseMixin):
    """Custom AjaxableResponseMixin

    Form with this mixin have to return an ID and new merchant title.

    Returns:
      JSON, like this:
        {
          "pk": 12,
          "merchant": "Yandex LLC",
        }

    """

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'merchant': self.object.merchant.official_name,
                'url': self.object.merchant.get_absolute_url(),
            }
            return JsonResponse(data)
        else:
            return response


class TrackerList(CustomLoginRequiredMixin, ListView):
    """All ISO's trackers list.

    List of all ISO's trackers with 30 mentions per a tracker.

    """
    model = Tracker
    template_name = 'iso/trackers.html'
    context_object_name = 'trackers'

    def get_queryset(self):
        """Accessing to account merchants list.

        Returns:
          QuerySet: merchants that user have access to

        """
        user = self.request.user
        return self.model.objects.filter(
            merchant_id__in=user.account.merchants.values_list('id', flat=True)
        )

    def get_context_data(self, **kwargs):
        """Adds TrackerModelForm to template context

        Adds TrackerModelForm and set initial values to the form.

        """
        user = self.request.user
        # Initial values for TrackerAddForm. All checkboxes are choiced.
        initial = {'social_networks': [s[0] for s in Tracker.SOCIAL_CHOICES]}
        form = TrackerModelForm(initial=initial)
        # Adds ordered by official name account's merchants to form.
        merchants = user.account.merchants.order_by('official_name')
        form.fields['merchant'].queryset = merchants

        context = super().get_context_data(**kwargs)
        context['merchants'] = merchants
        context['form'] = form
        return context


class TrackerCreateView(CustomLoginRequiredMixin, TrackerAjaxableResponseMixin,
                        CreateView):
    """Form to create new Tracker

    New traker is creating using ajax. Returns tracker ID.

    Returns:
      JSON with errors and new merchant ID if form valid

    """
    model = Tracker
    form_class = TrackerModelForm
    template_name = 'iso/trackers/tracker_form.html'

    def get_success_url(self):
        """If tracker added, returns tracker's list
        """
        return reverse('mentions:trackers')

    def form_valid(self, form, **kwargs):
        """Action if form is valid

        Args:
          form: form

        """
        form.instance.account = self.request.user.account
        return super().form_valid(form)


class TrackerUpdateView(CustomLoginRequiredMixin, TrackerAjaxableResponseMixin,
                        UpdateView):
    """Form to update Tracker

    The tracker is updating using ajax. Returns tracker ID.

    """
    model = Tracker
    form_class = TrackerModelForm
    template_name = 'iso/trackers/tracker_form.html'

    def get_success_url(self):
        """If tracker added, returns tracker's list
        """
        return reverse('mentions:trackers')

    def form_valid(self, form, **kwargs):
        """Action if form is valid

        Args:
          form: form

        """
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Adds TrackerModelForm to template context.
        Adds TrackerModelForm and set custom merchants
        queryset with account's merchans.
        """
        user = self.request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Adds ordered by official name account's merchants to form.
        merchants = user.account.merchants.order_by('official_name')
        form.fields['merchant'].queryset = merchants

        context = super().get_context_data(**kwargs)
        context['form'] = form
        return context


class TrackerDeleteView(CustomLoginRequiredMixin, AjaxableResponseMixin,
                        DetailView):
    """Delete a tracker using AJAX or HTTP query.

    Only account member can delete the Tracker.

    Returns:
      JSON if success, and standart HTTP error code if fail.

    """
    model = Tracker

    def get_queryset(self):
        return self.request.user.account.trackers.all()

    def get(self, request, *args, **kwargs):
        tracker = self.get_object()
        tracker.delete()
        context_dict = {
            'success': True
        }

        return JsonResponse(context_dict)


class TrackerMentionsListView(CustomLoginRequiredMixin, SingleObjectMixin,
                              ListView):
    """Getting a paginated mentions list.

    The mentions list uses in trackers page and getting with AJAX.

    Returns:
      QuerySet: Mention's queryset. Filter by social networks and status

    """
    paginate_by = 30
    template_name = "iso/trackers/mentions_list.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Tracker.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Mention.objects.filter(
            merchant_id=self.object.merchant_id,
            origin_site__in=self.object.social_networks).exclude(
            status__in=[Mention.NOT_ANALYSED])
