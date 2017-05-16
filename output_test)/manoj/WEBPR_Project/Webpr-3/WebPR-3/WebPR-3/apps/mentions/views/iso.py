"""
All views related to iso dashboards
"""
import re
import isoweek
import json
from hashlib import md5
from random import randint
from datetime import datetime, timedelta
from contextlib import suppress
from collections import namedtuple
from calendar import monthrange
from operator import itemgetter

from django.shortcuts import render
from django.views.generic import (ListView, TemplateView, CreateView,
                                  FormView, View)
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponse
from django.forms.utils import ErrorList
from django.db.models import Q, Sum
from django.core.files.storage import default_storage

from dateutil import relativedelta
from braces.views import CsrfExemptMixin

from apps.mentions.models import Mention, Merchant, Rating, ToDo, Category
from apps.mentions.forms.forms import AddMerchantForm
from apps.mentions.utils.flynsarmy_paginator.flynsarmy_paginator import \
    FlynsarmyPaginator
from apps.mentions.admin.forms import ImportMerchantsForm
from apps.mentions.tasks import bulk_merchant_import
from apps.users.models import AppUser
from libs.views.mixins import AjaxableResponseMixin
from .mixins import CustomLoginRequiredMixin

__all__ = ['DashboardView', 'ComplaintsView', 'AddMerchantView',
           'SolvedTodoView', 'BigFiveView', 'MentionsChartView', 'ScoreView',
           'LowestRankedMerchantsView', 'BulkImportView',
           'ConfirmedMerchantImportView', 'SemantriaHookView',
           'IndustryComplaintsChartView', 'download_sample', ]

PERIOD_WEEK = 'week'
PERIOD_MONTH = 'month'
ALLOWED_PERIODS = [PERIOD_WEEK, PERIOD_MONTH]


def hexcolor(string):
    """Function for generate HEX color for charts.

    Args:
      string (string): String that will be hashed.

    Returns:
      (string): First 6 symbols from md5 hash of the string.

    """
    return '#' + md5(str(string).encode('utf-8')).hexdigest()[:6]


def download_sample(request):
    """Function to download sample .csv for bulk import of merchants.

    Args:
      request: HttpRequest object.

    Returns: (object):
      response

    """
    filename = 'bulk_import.csv'
    f = default_storage.open(filename).read()
    content_disposition = 'attachment; filename={0}'.format(filename)
    response = HttpResponse(f, content_type='application/force-download')
    response['Content-Disposition'] = content_disposition
    return response


def get_date_and_period(request):
    """Gets `date` and `period` from request.GET.

    Gets and prepare `date` and `period` for using.

    Args:
      request: HttpRequest object.

    Returns (tuple):
      date_and_period (namedtuple) with:
        date (datetime object): datetime from string or now.
        period (string): `week`, `month`, etc.

    """
    req_get = request.GET.get
    period = req_get('period', '').lower()
    period = period if period in ALLOWED_PERIODS else PERIOD_WEEK
    date = now()

    if req_get('date'):
        with suppress(ValueError):
            date = datetime.strptime(req_get('date'), '%d %m %y')

    DateAndPeriod = namedtuple('DateAndPeriod', ('date', 'period'))
    return DateAndPeriod(date=date, period=period)


def get_merchant_set(request, all=False):
    """All merchants according to request.

    The function should be received an arg `filter` from request.GET and
    returned an merchant's QuerySet.

    If this arg is category or is a SIC of a category (`keywordType`) - the
    function should be returned an all merchant's from the category QuerySet.

    If this arg is merchant's name - it should be returned a QuerySet.

    Args:
      request (object): Django's request object.
      all (boolean): option for selected all merchants, not account's only.

    Returns:
     (QuerySet): Merchant's QuerySet.

    """
    MERCHANT, CATEGORY = 'merchant', 'category'
    keyword = request.GET.get('filter', None)
    keyword_type = request.GET.get('keywordType', '').lower()
    qs = Q()

    if not all and keyword and (not keyword_type or keyword_type == MERCHANT):
        qs = qs & Q(official_name=keyword)
    elif keyword and keyword_type == CATEGORY:
        qs = qs & Q(category__code=keyword)

    if request.user.is_superuser or all:
        return Merchant.objects.filter(qs)
    else:
        return request.user.account.merchants.filter(qs)


def get_legend_for_period(date, period, iteration):
    """Get legend for date and period.

    Legend for a point of chart. Show label like: `3/28-4/3`
    or `11/1-11/30` if period is `month`.

    Args:
      date (datetime): Datetime object. A date for start the period.
      period (str): Period for the chart`s point, `week` or `month`.
      iteration (int): Number of point of the chart`s legend.

    Returns:
      (Str): Legend for selected period and date.

    """
    if period == PERIOD_WEEK:
        delta = relativedelta.relativedelta(weeks=iteration)
        yearweek = itemgetter(0, 1)
        week = isoweek.Week(*yearweek((date-delta).isocalendar()))
        start_date = week.monday()
        end_date = week.sunday()
        return '{0}/{1} - {2}/{3}'.format(start_date.month, start_date.day,
                                          end_date.month, end_date.day)
    else:
        delta = relativedelta.relativedelta(months=iteration)
        start_date = date - delta
        end_date = monthrange((date-delta).year, (date-delta).month)[1]
        return '{0}/{1} - {2}/{3}'.format(start_date.month, 1,
                                          start_date.month, end_date)


def filter_mentions(request):
    """Filter mentions by request.

    If the user has chaned date or date range, we should change complaint view.

    Args:
      request: request

    Returns:
      neg_mentions (list of Mention): Mentions matching date and period.

    """
    date, period = get_date_and_period(request)
    neg_mentions = list()
    merchants = get_merchant_set(request)
    negative = Mention.objects.get_mentions_for_period(
        merchants, date, period
    ).filter(
        sentiment=Mention.NEGATIVE
    ).order_by('-mention_date')

    if negative:
        neg_mentions.extend(negative)

    return neg_mentions


class DashboardView(CustomLoginRequiredMixin, ListView):
    """Dashboard for ISO.

    Main ISO's page with widgets, sort and search tools.

    """
    template_name = 'iso/dashboard/dashboard.html'
    context_object_name = 'merchants'

    def get_context_data(self, **kwargs):
        """Providing custom data into context.

        Adds to context form for Adding Merchant and categories set (only
          unique) for search.

        Returns:
          context (dict): Updated context with our's data.

        """
        context = super().get_context_data(**kwargs)
        context['form'] = AddMerchantForm
        context['import_form'] = ImportMerchantsForm
        context['categories'] = {m.category for m in self.get_queryset() if
                                 m.category}
        return context

    def get_queryset(self):
        """Method that returns custom queryset of the view.

        If we have an access we can get all merchants, related to this account.
        Otherwise we will raise PermissionDenied.

        Returns:
          QuerySet if not raised a PermissionDanied exception.

        """
        if self.request.user.is_superuser:
            return Merchant.objects.prefetch_related('category').order_by(
                'official_name')
        elif self.request.user.is_iso:
            return self.request.user.account.merchants.prefetch_related(
                'category').order_by('official_name')
        else:
            raise PermissionDenied


class ComplaintsView(CustomLoginRequiredMixin, ListView):
    """
    View to load complaints with filter by merchant / period
    """
    template_name = 'iso/dashboard/complaints.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        """
        Function to get all negative complaints about all (or certain)
        merchants, related to current account.

        Returns:
            mentions (list of Mentions): not more than 10 mentions overall
        """
        return filter_mentions(self.request)[0:10]


class AddMerchantView(CustomLoginRequiredMixin, AjaxableResponseMixin,
                      CreateView):
    """View to create Merchant from ISO interface.

    View uses AjaxableResponseMixin for responses and requests with JSON.

    Attrs:
      form_class (object): A Django's form object. The form uses in view.
      template_name (str): Template name. Does not use in the view but
                           required as and attr.

    """
    form_class = AddMerchantForm
    template_name = ''

    def form_valid(self, form):
        """Form valid action.

        Args:
          form (object): A Django's form object.

        Returns:
          JSON response with HTTP 200. Contains: created merchant name,
          his category and code.

        """
        merchant = form.save(request=self.request)
        data = {
            'merchant': {
                'value': merchant.official_name
            }
        }
        if merchant.category:
            data['merchant'].update({
                'category': {
                    'value': merchant.category.name,
                    'code': merchant.category.code,
                },
            })
        return JsonResponse(data)

    def form_invalid(self, form):
        """Form invalid action.

        Args:
          form (object): A Django's form object.

        Returns:
          JSON response with HTTP 400. Contains serialized form errors.

        """
        if form.errors.as_data().get('web_page'):
            form.errors['web_page'] = ErrorList(['Enter a valid URL'])

        return JsonResponse(form.errors, status=400)


class SolvedTodoView(CustomLoginRequiredMixin, TemplateView):
    """
    View to display solved/unsolved diagram
    """

    def get_template_names(self):
        """
        Method to change template for rendering depends on requested dashboard
        """
        if self.request.path == '/response_rate_iso':
            return ['iso/dashboard/charts/response_rate.html']
        elif self.request.path == '/response_rate_merchant':
            return ['merchant/resolved_complaints.html']
        else:
            return ['iso/dashboard/charts/solved_unsolved.html']

    def get_todo_quantity(self):
        """Get count of Todo`s.

        Function to find count of solved to-do and count of all todo.

        Returns (namedtuple):
          solved (int): count of solved to-do.
          total (int): count of all to-do.
          change (bool): change from current to previous period.

        """
        solved = 0
        total = 0
        prev_solved = 0
        change = True
        date_and_period = get_date_and_period(self.request)
        date = date_and_period.date
        period = date_and_period.period
        merchants = get_merchant_set(self.request)

        if period in ALLOWED_PERIODS:
            todo_total, todo_solved = ToDo.objects.get_todo_count(
                merchants, date, period
            )
            total += todo_total
            solved += todo_solved
            # compare with previous period
            prev_date = date - timedelta(days=7)

            if period == PERIOD_MONTH:
                prev_date = date - timedelta(days=(date.day+1))

            prev_total, previous_solved = ToDo.objects.get_todo_count(
                merchants, prev_date, period
            )
            prev_solved += previous_solved

        if prev_solved > solved:
            change = False

        todo_quantity = namedtuple('todo_quantity', ('solved', 'total',
                                                     'change', 'period'))

        return todo_quantity(solved=solved, total=total, change=change,
                             period=period)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todo_quantity = self.get_todo_quantity()
        context['change'] = todo_quantity.change
        context['solved'] = todo_quantity.solved
        context['total'] = todo_quantity.total
        context['period'] = todo_quantity.period
        context['unsolved'] = todo_quantity.total - todo_quantity.solved

        if todo_quantity.total:
            context['rate'] = todo_quantity.solved / todo_quantity.total * 100
        else:
            context['rate'] = 0

        return context


class BigFiveView(CustomLoginRequiredMixin, TemplateView):
    """
    View to display the big five chart
    """
    template_name = 'iso/dashboard/charts/big_five.html'

    def get_context_data(self, **kwargs):
        """
        Method to display big five view
        """
        context = super().get_context_data(**kwargs)
        mentions = filter_mentions(self.request)
        total = len(mentions)
        context['total_complaints'] = total
        yelp = 0
        facebook = 0
        google = 0
        ripoffreport = 0
        bbb = 0

        for mention in mentions:
            site = mention.origin_site
            if site == Mention.YELP:
                yelp += 1
            elif site == Mention.FACEBOOK:
                facebook += 1
            elif site == Mention.GOOGLE:
                google += 1
            elif site == Mention.RIP:
                ripoffreport += 1
            elif site == Mention.BBB:
                bbb += 1

        # absolute values
        context['yelp'] = yelp
        context['facebook'] = facebook
        context['google'] = google
        context['ripoffreport'] = ripoffreport
        context['bbb'] = bbb

        # percent values
        if total > 0:
            context['yelp_per'] = yelp / total * 100
            context['facebook_per'] = facebook / total * 100
            context['google_per'] = google / total * 100
            context['ripoffreport_per'] = ripoffreport / total * 100
            context['bbb_per'] = bbb / total * 100

        return context


class MentionsChartView(CustomLoginRequiredMixin, View):
    """
    View to build mentions chart
    """
    def get_ratings(self):
        """
        Method to get ratings for Mention chart widget
        Returns:
            ratings (namedtuple):
                negative (list): list of negative mentions
                positive (list): list of positive mentions
                neutral (list): list of neutral mentions
        """
        negative, positive, neutral, legend = list(), list(), list(), list()
        merchants = get_merchant_set(self.request)
        date_and_period = get_date_and_period(self.request)
        date, period = date_and_period.date, date_and_period.period

        for i in reversed(range(7)):
            if period == PERIOD_WEEK:
                date_shift = date - relativedelta.relativedelta(weeks=i)
                neg, pos, neut = Rating.objects.get_mention_counts(
                    merchants=merchants,
                    year=date_shift.isocalendar()[0],
                    week=date_shift.isocalendar()[1]
                )
                negative.append(neg)
                positive.append(pos)
                neutral.append(neut)
            else:
                date_shift = date - relativedelta.relativedelta(months=i)
                neg, pos, neut = Rating.objects.get_mention_counts(
                    merchants=merchants,
                    year=date_shift.year,
                    month=date_shift.month
                )
                negative.append(neg)
                positive.append(pos)
                neutral.append(neut)
            # add legend for the point
            legend.append(get_legend_for_period(date, period, i))

        ratings = namedtuple('ratings', ('negative', 'positive', 'neutral',
                                         'legend'))
        return ratings(negative=negative, positive=positive, neutral=neutral,
                       legend=legend)

    def get(self, request, *args, **kwargs):
        ratings = self.get_ratings()
        return JsonResponse({
            'is_success': True,
            'negative': ratings.negative,
            'positive': ratings.positive,
            'neutral': ratings.neutral,
            'legend': ratings.legend
        })


class ScoreView(CustomLoginRequiredMixin, View):
    """
    View to show score for merchant or for merchant/industry in ISO dashboard
    """
    def get_all_merchant_score(self, date, period):
        """Function to calculate rating for all merchants.

        Args:
          date (datetime): date to initiate calculation.
          period (str): period to calculate rating for.

        Returns:
          res (float): average rating for all merchants.

        """
        total_score = list()
        res = 0

        if self.request.user.is_superuser:
            merchants = Merchant.objects.all()
        else:
            merchants = self.request.user.account.merchants.all()

        rating = Rating.objects.get_rating_for_period(merchants, date, period)
        if rating:
            for score in rating:
                total_score.append(score.rating)
        if total_score:
            res = int(sum(total_score) / len(total_score))
        return res

    def get_all_industry_score(self, date, period):
        """Function to calculate rating for all industry.

        Args:
          date (datetime): date to initiate calculation.
          period (str): period to calculate rating for.

        Returns:
          res (float): average rating for merchants into given industry.

        """
        total_score = list()
        res = 0

        all_merchants = Merchant.objects.all()

        rating = Rating.objects.get_rating_for_period(all_merchants, date,
                                                      period)
        if rating:
            for score in rating:
                total_score.append(score.rating)
        if total_score:
            res = int(sum(total_score) / len(total_score))
        return res

    def get_merchant_score(self, date, period):
        """
        Function to calculate rating for merchant
        Args:
            date (datetime): date to initiate calculation
            period (str): period to calculate rating for
        Returns:
            res (float): average rating for merchants
        """
        total_score = []
        res = 0
        merchants = get_merchant_set(self.request)
        rating = Rating.objects.get_rating_for_period(merchants, date, period)
        if rating:
            for score in rating:
                total_score.append(score.rating)
        if total_score:
            res = round((sum(total_score) / len(total_score)), 0)
        return res

    def get_industry_score(self, date, period):
        """Function to calculate rating for industry.

        Args:
          date (datetime): date to initiate calculation.
          period (str): period to calculate rating for.

        Returns:
          res (float): average rating for merchants into given industry.

        """
        total_score = list()
        res = 0

        if not self.request.GET.get('filter'):
            all_merchants = Merchant.objects.all()
        else:
            merchants = get_merchant_set(self.request)
            industries = Category.objects.filter(
                merchants__in=merchants).distinct()
            all_merchants = Merchant.objects.filter(category__in=industries)

        rating = Rating.objects.get_rating_for_period(all_merchants, date,
                                                      period)
        if rating:
            for score in rating:
                total_score.append(score.rating)
        if total_score:
            res = round((sum(total_score) / len(total_score)), 0)
        return res

    def get_chart_data(self):
        """
        Method to calculate 7 points for performance tracking charts
        both in iso and merchant interfaces
        Returns:
            merchant_points (list): points of 7 weeks (or months) for merchant
            industry_points (list): points of 7 weeks (or months) for industry
        """
        date_and_period = get_date_and_period(self.request)
        date, period = date_and_period.date, date_and_period.period
        (merchant_points, industry_points, all_merchant_points,
         all_industry_points, legend) = list(), list(), list(), list(), list()
        # reversed because chart needs starting data displays from past time
        for i in reversed(range(7)):
            delta = relativedelta.relativedelta(months=i)

            if period == PERIOD_WEEK:
                delta = relativedelta.relativedelta(weeks=i)

            shifted_date = date - delta

            all_merchant_points.append(
                self.get_all_merchant_score(shifted_date, period))
            all_industry_points.append(
                self.get_all_industry_score(shifted_date, period))
            merchant_points.append(
                self.get_merchant_score(shifted_date, period))
            industry_points.append(
                self.get_industry_score(shifted_date, period))
            # add legend for the point
            legend.append(get_legend_for_period(date, period, i))

        chart_data = namedtuple('chart_data', ('all_merchant_points',
                                               'all_industry_points',
                                               'merchant_points',
                                               'industry_points',
                                               'legend'))

        return chart_data(merchant_points=merchant_points,
                          industry_points=industry_points,
                          all_merchant_points=all_merchant_points,
                          all_industry_points=all_industry_points,
                          legend=legend)

    def get_average_rating(self):
        """
        Method to retrieve avreage rating for merchant and industry
        Returns:
            average_rating (namedtuple):
                merchant_rating (int): Rating for merchant
                industry_rating (int): Rating for industry
        """
        merchant_rating = self.get_merchant_score(now(), PERIOD_WEEK)
        industry_rating = self.get_industry_score(now(), PERIOD_WEEK)
        average_rating = namedtuple('average_rating', (
            'merchant_rating', 'industry_rating'))
        return average_rating(merchant_rating=merchant_rating,
                              industry_rating=industry_rating)

    def get(self, request, *args, **kwargs):
        """Gets and prepares chart`s data for response.

        Gets data for response`s queries, prepares and sets all to JSON.
        After frontend refactoring the method has to returns `scores` list
        with data for charts.

        Returns:
          JsonResponse

        """
        CATEGORY = 'category'
        MERCHANT = 'merchant'
        YOU = 'You'
        YOUR_MERCHANTS = 'Your merchants'
        ALL_MERCHANTS = 'All merchants'
        req_get = self.request.GET.get
        keyword = req_get('filter', '').strip()
        keyword_type = req_get('keywordType', '').lower()
        qs = Q()
        your = 'Your merchants'
        all = 'All merchants'
        scores = []
        chart_data = self.get_chart_data()
        average_rating = self.get_average_rating()

        # if `date` - it is an ISO and needs more charts
        if req_get('date', None):
            scores.extend([{
                'label': YOUR_MERCHANTS,
                'data': chart_data.all_merchant_points,
                'color': '#0fb474'
            }, {
                'label': ALL_MERCHANTS,
                'data': chart_data.all_industry_points,
                'color': '#f89a1c'
            }])

        if keyword and keyword_type == CATEGORY:
            qs = qs & Q(code=keyword)
        elif keyword and keyword_type == MERCHANT:
            qs = qs & Q(merchants__official_name=keyword)
            your = keyword
            if not req_get('date', None):
                your = YOU
            scores.append({
                'label': your,
                'data': chart_data.merchant_points,
                'color': '#3d80cb'
            })

        category = Category.objects.filter(qs).first()

        if category and keyword_type == CATEGORY:
            your = 'Your {0}'.format(category.name)
            all = 'All {0}'.format(category.name)
            scores.extend([{
                'label': your,
                'data': chart_data.merchant_points,
                'color': '#3d80cb'
            }, {
                'label': all,
                'data': chart_data.industry_points,
                'color': '#b4051b'
            }])
        elif category and keyword_type == MERCHANT:
            all = category.name
            scores.extend([{
                'label': all,
                'data': chart_data.industry_points,
                'color': '#b4051b'
            }])

        return JsonResponse({
            'is_success': True,
            'merchant_score': chart_data.merchant_points,
            'industry_score': chart_data.industry_points,
            'x_legend': chart_data.legend,
            'merchant': your,
            'industry': all,
            'scores': scores,
            'avg_merchant': average_rating.merchant_rating,
            'avg_industry': average_rating.industry_rating,
            'has_industry': True if category else False
        })


class LowestRankedMerchantsView(CustomLoginRequiredMixin, ListView):
    """View for showing Lowest Ranked Merchants

    https://jingru.saritasa.com/boris/index.php?name=2016-01-29_1655.png
    List must be paginated and filtered by date range
    """
    template_name = 'iso/dashboard/tables/lowest_ranked.html'
    page_kwarg = 'page'
    paginator_class = FlynsarmyPaginator
    paginate_by = 5
    adjacent_pages = 2  # parameter for FlynsarmyPaginator

    def get_paginator(self, *args, **kwargs):
        """Adds kwarg `adjacent_pages` to `ListView.get_paginator`

        Returns:
            instance of the paginator for this view.
        """
        kwargs.update({'adjacent_pages': self.adjacent_pages})
        return super().get_paginator(*args, **kwargs)

    def get_queryset(self):
        """Get Ratings (with fk to merchant) according to requested date.

        Each Rating will be annotated with
            .trend - list of 5 last ratings (montly or weekly), and
                last rating will be current
                (i.e. 4 previous and 1 last rating)
            .is_trend_positive - boolean to show if last rating is better
                then previous (red and green triangles in the template)
        """
        date_and_period = get_date_and_period(self.request)
        date, self.period = date_and_period
        year, week_number, day_number = date.isocalendar()
        # Get actual merchants and it's ratings
        if self.period == PERIOD_WEEK:
            qs = Rating.objects.filter(week=week_number, year=year)
            # set filter to monday 4 weeks ago
            four_periods_ago = date - timedelta(days=date.weekday(), weeks=4)
            old_ratings_filter = {'month__isnull': True}
        else:
            qs = Rating.objects.filter(month=date.month, year=date.year)
            four_periods_ago = date - relativedelta.relativedelta(months=4)
            # set filter to first day of that month
            four_periods_ago = datetime(
                four_periods_ago.year, four_periods_ago.month, 1)
            old_ratings_filter = {'week__isnull': True}

        # set time to midnight
        four_periods_ago = four_periods_ago.replace(
            hour=0, minute=0, second=0, microsecond=0)

        # filter merchants according to ISO
        if not self.request.user.is_superuser:
            qs = qs.filter(
                merchant__in=self.request.user.account.merchants.all())
        qs = qs.order_by('rating')

        old_ratings_filter.update({
            'created__gte': four_periods_ago,
            'created__lte': date
        })

        for rating in qs:
            # Get ratings for this merchant for last 4 peroids excluding
            # current
            old_ratings = rating.merchant.ratings.filter(
                **old_ratings_filter).exclude(id=rating.id).order_by('created')

            rating.trend = [r.rating for r in old_ratings]

            # add last rating to trend
            rating.trend.append(rating.rating)
            # adjsut trend to always contain 5 items
            if len(rating.trend) < 5:
                rating.trend = [0] * (5 - len(rating.trend)) + rating.trend

            # define if trend is positive.
            # trend is positive if current rating is greater then previous
            rating.is_trend_positive = bool(
                rating.trend[-1] >= rating.trend[-2])
        return qs

    def get_context_data(self, **kwargs):
        """Add period to context.

        Used to display `4-week trend` or `4-month trend` as header for third
        column of the table
        """
        context = super().get_context_data(**kwargs)
        context['period'] = self.period
        return context


class BulkImportView(CustomLoginRequiredMixin, FormView):
    """
    View to process form with bulk merchants import
    """
    form_class = ImportMerchantsForm
    template_name = 'iso/import.html'

    def form_valid(self, form):
        """
        Add list of fields to create merchants into session
        """
        self.request.session['raw_data'] = form.merchants
        ctx = {}
        ctx['parsed'] = len(form.merchants)
        ctx['failed_validation'] = form.validation_errors
        return render(request=self.request,
                      template_name='iso/confirm_creation.html',
                      context=ctx)

    def form_invalid(self, form):
        """Invalid stateiment for the import form.

        If .csv file is invalid, override the error message to be more user.
        friendly.

        """
        if form.errors.as_data().get('csv_file'):
            form.errors['csv_file'] = ErrorList(
                ['Your file has incorrect format or data']
            )
        return super().form_invalid(form)


class ConfirmedMerchantImportView(CustomLoginRequiredMixin, TemplateView):
    """Additional view to make Merchant and AppUser objects from parsed .csv
    This view gives user validation errors in table and suggests choice -
    start import or step back and correct mistakes in .csv.
    """
    template_name = 'iso/confirmed.html'

    def import_merchants(self):
        """Method to create objects from parsed .csv.

        CSV will be retrieved from session

        Returns:
          ctx (dict): context objects to show user success message

        """
        created_merchants = list()
        created_users = list()
        merchants = self.request.session['raw_data']
        for merch_info in merchants:
            category = Category.objects.filter(
                Q(name__iexact=merch_info['industry_name']) |
                Q(code=merch_info['industry_name'])).first()
            merchant, _ = Merchant.objects.get_or_create(
                official_name=merch_info['official_name'])
            merchant.short_name = [merch_info['short_name0'],
                                   merch_info['short_name1'],
                                   merch_info['short_name2']]
            merchant.address = merch_info['address']
            merchant.city = merch_info['city']
            merchant.state = merch_info['state']
            merchant.zip_code = merch_info['zip_code']
            merchant.contact_info = merch_info['contact_info']
            merchant.phone = [merch_info['phone0'],
                              merch_info['phone1'],
                              merch_info['phone2']]
            merchant.product = [merch_info['product0'],
                                merch_info['product1'],
                                merch_info['product2']]
            merchant.web_page = [merch_info['web_page0'],
                                 merch_info['web_page1'],
                                 merch_info['web_page2'],
                                 merch_info['web_page3'],
                                 merch_info['web_page4']]
            merchant.ceo = [merch_info['ceo0'],
                            merch_info['ceo1'],
                            merch_info['ceo2']]
            merchant.dda = merch_info['dda']
            merchant.sources = merch_info['sources']
            if category:
                merchant.category = category
            created_merchants.append(merchant)
            if merch_info['user_email']:
                username = '{}_{}_user'.format(merchant.official_name[0:10],
                                               randint(0, 100))
                user = AppUser()
                user.email = merch_info['user_email']
                p = re.compile(r'\W(?!\s)\W*')
                username = p.sub('_', username)
                user.username = username
                created_users.append(user)
        ctx = {}
        ctx['merchants'] = len(created_merchants)
        # assign new merchants to selected ISO account
        iso_account = self.request.user.account
        iso_account.merchants.add(*created_merchants)
        # if there are a few merchants - we will save it on-the-fly
        if len(created_merchants) < 10000:
            ctx['save_method'] = ('merchants and users were succussfully '
                                  'added/updated')
            bulk_merchant_import(created_merchants, created_users,
                                 self.request)
        # otherwise we should start the celery job
        else:
            ctx['save_method'] = ('merchants and users will be added/updated '
                                  'during few minutes')
            bulk_merchant_import.delay(created_merchants, created_users,
                                       self.request)
        return ctx

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.import_merchants())
        return context


class SemantriaHookView(CsrfExemptMixin, View):
    """
    Web hook to obtain data from Semantria after analysis
    """

    def post(self, request, *args, **kwargs):
        """Method to process semantria callback.

        Args:
          request: Http request

        Returns:
          HttpResponse

        """
        results = json.loads(request.body.decode('utf-8'))
        mentionsSentiment = []
        for result in results:
            sentiment = {'sentiment': result.get('sentiment_polarity'),
                         'mention_text': result.get('summary'),
                         'sentiment_value': result.get('sentiment_score'),
                         'u_id': result.get('id')}
            mentionsSentiment.append(sentiment)
        Mention.objects.update_mentions(mentionsSentiment)
        return HttpResponse()


class IndustryComplaintsChartView(CustomLoginRequiredMixin, View):
    """View to show Industries complaints chart.

    Shows chart with industries, that comprise majority of negative mentions.

    """

    def get(self, request, *args, **kwargs):
        """Get data for Industry`s Complaints Chart.

        Returns:
          JSON: data for the chart.

        """
        qs = Q()
        labels = []
        datasets = {
            'data': [],
            'extData': [],
            'backgroundColor': []
        }
        params = get_date_and_period(request)
        period = params.period
        filter_values = {
            PERIOD_WEEK: params.date.isocalendar()[1],
            PERIOD_MONTH: params.date.month
        }

        if not request.user.is_superuser:
            qs = qs & Q(account__id=request.user.account_id)

        ids = Merchant.objects.filter(qs).values_list('id', flat=True)

        filter_kwargs = {
            'merchants__id__in': ids,
            'merchants__ratings__year': params.date.year,
            'merchants__ratings__{0}'.format(period): filter_values[period]
        }

        categories = Category.objects.filter(**filter_kwargs).annotate(
            neg=Sum('merchants__ratings__neg_mentions'),
            tot=Sum('merchants__ratings__mentions_count')
        ).values('name', 'code', 'neg', 'tot')

        for cat in categories.filter(neg__gt=0):
            labels.append('{0} - {1}'.format(cat['code'], cat['name']))
            datasets['data'].append(cat['neg'])
            # calc and add percentage of negative mentions from total count
            # for the industry
            datasets['extData'].append((100 / cat['tot']) * cat['neg'])
            datasets['backgroundColor'].append(hexcolor(cat.get('code', '')))

        return JsonResponse({
            'labels': labels,
            'datasets': datasets
        })
