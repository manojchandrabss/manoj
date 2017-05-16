import json

from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.utils import timezone

from apps.mentions.models import *
from apps.mentions.views.iso import *
from apps.mentions.views.merchant import *
from apps.mentions.tests.factories import (UserFactory, AccountFactory,
                                           MerchantFactory, MentionFactory)
from apps.users.models import Account


class TestMerchantDetail(TestCase):
    """Test of Merchant detail view.

    Tests for Merchant's dashboard.

    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)
        self.merchant = MerchantFactory()
        self.merchant.account_set.add(self.account)

    def test_view(self):
        """
        Test of 200 ok status code for this view
        """
        request = self.factory.get('')
        request.user = self.user
        response = MerchantDetail.as_view()(request, pk=self.merchant.id)
        self.assertEqual(response.status_code, 200)


class TestToDo(TestCase):
    """Tests for Todo's views.

    Test views whose are related to Todo model. Create, update, delete etc.

    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory(type=Account.MERCHANT)
        self.user = UserFactory(account=self.account,
                                last_login=timezone.now())
        self.merchant = MerchantFactory()
        self.merchant.account_set.add(self.account)
        self.mention = MentionFactory(merchant=self.merchant)

    def test_create_todo(self):
        """Test for create Todo.

        Create Todo for a mention in merchant dashboard.

        """
        due_date = timezone.now() + timedelta(days=1)
        data = {
            'user': self.user.id,
            'mention_uid': self.mention.u_id,
            'company': self.merchant.id,
            'priority': 0,
            'due_date': due_date.strftime('%Y-%m-%d'),
        }
        request = self.factory.post(reverse('mentions:addtodo'), data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = AddToDoView.as_view()(request)
        response_json = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual('pk' in response_json.keys(), True)

    def test_update_todo(self):
        """Test for update Todo.

        This uses in merchant's dashboard for update status and rating.

        """
        todo = ToDo.objects.create(mention=self.mention)
        request = self.factory.get('')
        request.user = self.user
        response = UpdateToDo.as_view()(request, pk=todo.id)
        self.assertEqual(response.status_code, 200)
