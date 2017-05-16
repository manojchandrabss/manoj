import json
import factory

from django.test import TestCase, RequestFactory
from django.utils import timezone

from unittest import TestCase

from apps.mentions.models import *
from apps.mentions.tests.factories import (
    UserFactory, AccountFactory, MerchantFactory, TrackerFactory,
    WeekRatingFactory, MonthRatingFactory, setup_view
)
from apps.mentions.views import *


class TestDashboardView(TestCase):
    """
    Test class for dashboard view
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory(type=Account.ISO)
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = DashboardView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestLowestRankedMerchants(TestCase):
    """
    Test for lowest ranked merchants
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = LowestRankedMerchantsView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestAddMerchantView(TestCase):
    """
    Test for add merchant form
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)
        self.merchant = MerchantFactory()
        self.merchant.account_set.add(self.account)

    def test_post(self):
        """
        Test to check if merchant added successfully
        """
        data = {'official_name': factory.Faker('company').generate({})}
        request = self.factory.post(reverse('mentions:add_merchant'), data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = AddMerchantView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class TestTracker(TestCase):
    """Test for tracker's views.

    Very simple tests. Need to improvements.

    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.merchant = MerchantFactory()
        self.tracker = TrackerFactory(merchant=self.merchant,
                                      account=self.account)
        self.user = UserFactory(account=self.account)

    def test_tracker_list(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = TrackerList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_tracker_mentions_list(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        response = TrackerMentionsListView.as_view()(request,
                                                     pk=self.tracker.id)
        self.assertEqual(response.status_code, 200)

    def test_tracker_create(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = TrackerCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_tracker_update(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = TrackerUpdateView.as_view()(request, pk=self.tracker.id)
        self.assertEqual(response.status_code, 200)

    def test_tracker_delete(self):
        """
        Test of success var in json returns for this view
        """
        request = self.factory.get('', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = TrackerDeleteView.as_view()(request, pk=self.tracker.id)

        self.assertEqual(response.content, b'{"success": true}')


class TestMentionsChartView(TestCase):
    """
    Test of mentions chart view
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = MentionsChartView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestBigFiveView(TestCase):
    """
    Test of big five view
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = BigFiveView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestSolvedTodoView(TestCase):
    """
    Test of solved to-do view
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = SolvedTodoView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestComplaintsView(TestCase):
    """
    Test for complaints widget
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = ComplaintsView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestScoreView(TestCase):
    """
    Test of score view
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        view = ScoreView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_merchant_score(self):
        """
        test get_merchant_score method - NOT COMPLETE!
        """
        request = self.factory.get('')
        request.user = self.user
        request.period = 'week'
        request.date = timezone.now()
        view = setup_view(ScoreView(), request)
        res = view.get_merchant_score(date=request.date, period='week')
        self.assertGreaterEqual(res, 0)
