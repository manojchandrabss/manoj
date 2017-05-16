from operator import itemgetter

from django.views.generic import (View, ListView)
from django.db.models import Count
from django.http import JsonResponse

from dateutil import relativedelta

from apps.mentions.models import Merchant, Mention
from apps.mentions.views.mixins import CustomLoginRequiredMixin
from apps.mentions.views.iso import (get_date_and_period, get_merchant_set,
                                     get_legend_for_period, PERIOD_MONTH)


def get_complaints_by_source(merchants, date, period):
    """Get complaints by source.

    Method to return a list of dicts wit following structure:
      {
        'cnt' (int): count of complaints,
        'origin_site' (str): origin site of complaints
      }

    Args:
      merchants (list): list of merchants.
      date (datetime): datetime from string or now.
      period (string): `week`, `month`, etc.

    Returns:
      origin_sites (namedtuple): results of the query.

    """
    results = list()

    origin_sites = Mention.objects.get_mentions_for_period(
        merchants, date, period
    ).filter(
        sentiment=Mention.NEGATIVE
    ).values(
        'origin_site'
    ).annotate(
        cnt=Count('origin_site'),
        merchant=Count('merchant', distinct=True)
    ).order_by('origin_site')

    for site in Mention.TARGET_SITES:
        results.insert(0, {
            'merchant': 0,
            'cnt': 0,
            'origin_site': site[0]
        })

        if origin_sites:
            for i in origin_sites:
                if i['origin_site'] == site[0]:
                    results[0] = i

    return results


class StatisticsView(CustomLoginRequiredMixin, ListView):
    """Blank view for statistics page.

    The page will show ext statistics data for ISO.

    """
    template_name = 'statistics/statistics.html'
    context_object_name = 'merchants'

    def get_context_data(self, **kwargs):
        """Providing categories list into context.

        Returns:
          context (dict): Updated context with our's data.

        """
        context = super().get_context_data(**kwargs)
        # set of categories, only unique
        context['categories'] = {
            m.category for m in self.get_queryset() if m.category
        }
        return context

    def get_queryset(self):
        """Method that returns custom queryset of the view.

        Returns:
          QuerySet if not raised a PermissionDanied exception.

        """
        if self.request.user.is_superuser:
            return Merchant.objects.prefetch_related('category').order_by(
                'official_name')
        elif self.request.user.is_iso:
            return self.request.user.account.merchants.prefetch_related(
                'category').order_by('official_name')


class ComplaintsBySource(CustomLoginRequiredMixin, View):
    """Data for `Complaints By Source` widget

    Makes and responses data for the chart.

    """

    def get(self, request, *args, **kwargs):
        """Send response

        Returns: JSON

        """
        date_and_period = get_date_and_period(request)
        merchant_data = []
        labels = []
        avg_data = []
        avg_merchants = get_merchant_set(request, all=True)
        avg_complaints = get_complaints_by_source(avg_merchants,
                                                  date_and_period.date,
                                                  date_and_period.period)
        merchants_count = avg_merchants.count()

        for item in avg_complaints:
            avg = 0
            if merchants_count:
                avg = int(round((item['cnt']/merchants_count), 0))
            item['avg'] = avg

        for complaint in avg_complaints:
            source = Mention.SOURCES[complaint['origin_site']]
            labels.append(source.get('label'))
            avg_data.append(complaint['avg'])

        merchants = get_merchant_set(request)

        merchant_complaints = get_complaints_by_source(merchants,
                                                       date_and_period.date,
                                                       date_and_period.period)

        for complaint in merchant_complaints:
            merchant_data.append(complaint['cnt'])

        return JsonResponse({
            'labels': labels,
            'average': avg_data,
            'merchant': merchant_data,
        })


class ComplaintsOverTime(CustomLoginRequiredMixin, View):
    """Data for `Complaints Over Time` widget.

    Makes and responses data for the chart.

    """

    def get(self, request, *args, **kwargs):
        """Get data

        Returns: JSON

        """
        date_and_period = get_date_and_period(request)
        merchants = get_merchant_set(request)
        legend = []
        datasets = []
        sitegetter = itemgetter(0)
        data = {sitegetter(s): [] for s in Mention.TARGET_SITES}

        # reversed because chart needs starting data displays from past time
        for i in reversed(range(7)):
            delta = relativedelta.relativedelta(weeks=i)

            if date_and_period.period == PERIOD_MONTH:
                delta = relativedelta.relativedelta(months=i)

            shifted_date = date_and_period.date - delta

            complaints = get_complaints_by_source(merchants, shifted_date,
                                                  date_and_period.period)
            for complaint in complaints:
                data[complaint['origin_site']].append(complaint['cnt'])

            legend.append(
                get_legend_for_period(date_and_period.date,
                                      date_and_period.period, i))

        for k in data.keys():
            source = Mention.SOURCES[k]

            datasets.append({
                'label': source.get('label'),
                'data': data.get(k, []),
                'color': source.get('color', '#000')
            })

        return JsonResponse({
            'datasets': datasets,
            'legend': legend
        })
