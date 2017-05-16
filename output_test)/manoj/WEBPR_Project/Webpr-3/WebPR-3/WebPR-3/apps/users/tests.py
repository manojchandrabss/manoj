import json
from django.core.urlresolvers import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory

from faker import Faker

from apps.users.views import CreateUserForMerchant                                # flake8: noqa
from apps.mentions.tests.factories import (UserFactory, AccountFactory,
                                           MerchantFactory)

fake = Faker()


class TestUserViews(TestCase):
    """Test for create a User for Merchant.

    This test is testing views that related to the User model.

    """

    def setUp(self):
        self.factory = RequestFactory()
        self.account = AccountFactory()
        self.user = UserFactory(account=self.account)
        self.merchant = MerchantFactory()
        self.merchant.account_set.add(self.account)

    def test_create_user_for_merchant(self):
        """Test for CreateUserForMerchant view.

        Test is simple. It sends data for required fields and is checking
        JSON response, that has to return 'success' if form is valid.

        """
        data = {
            'username': fake.user_name(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'merchant': self.merchant.id
        }
        request = self.factory.post(reverse('users:create_user'), data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        request.session = {}
        # a bug with messages if request made with RequestFactory,
        # without it there is raise MessageFailure
        setattr(request, '_messages', FallbackStorage(request))
        response = CreateUserForMerchant.as_view()(request)
        self.assertEqual(response.status_code, 200)
