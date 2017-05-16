import factory
import uuid
import random
from apps.mentions.models import Merchant, Mention, Tracker, Rating
from apps.users.models import AppUser, Account


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class TrackerFactory(factory.django.DjangoModelFactory):
    """Factory for generates test Tracker model.

    Auto generates with a `social_networks` set.

    """

    class Meta:
        model = Tracker

    social_networks = [s[0] for s in Mention.TARGET_SITES]


class MentionFactory(factory.django.DjangoModelFactory):
    """Factory for generates test Mention model.

    Auto generates with custom u_id.

    """

    class Meta:
        model = Mention

    u_id = str(uuid.uuid4()).replace("-", "")


class MerchantFactory(factory.django.DjangoModelFactory):
    """Factory for generates test Merchant model.
    """

    class Meta:
        model = Merchant

    official_name = factory.Faker('company')
    short_name = [factory.Faker('company'), factory.Faker('company'),
                  factory.Faker('company')]
    web_page = [factory.Faker('url'), ]
    address = factory.Faker('street_address')


class AccountFactory(factory.django.DjangoModelFactory):
    """Factory for generates test Account model.

    Default it does not have a `type` attr.

    """

    class Meta:
        model = Account


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for generates test AppUser model.

    There are required fields first_name, last_name, username and email.

    """

    class Meta:
        model = AppUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('user_name')
    email = factory.Faker('email')


class WeekRatingFactory(factory.django.DjangoModelFactory):
    """
    Factory to generate fake rating for week
    """

    class Meta:
        model = Rating

    merchant = MerchantFactory()
    year = factory.Faker('year')
    week = random.randint(1, 53)
    mentions_count = random.randint(0, 1000)
    pos_mentions = random.randint(0, mentions_count)
    neg_mentions = random.randint(0, (mentions_count - pos_mentions))
    open_todo = random.randint(0, 500)
    solved_todo = random.randint(0, open_todo)


class MonthRatingFactory(factory.django.DjangoModelFactory):
    """
    Factory to generate fake rating for month
    """

    class Meta:
        model = Rating

    merchant = MerchantFactory()
    year = factory.Faker('year')
    month = random.randint(1, 12)
    mentions_count = random.randint(0, 1000)
    pos_mentions = random.randint(0, mentions_count)
    neg_mentions = random.randint(0, (mentions_count - pos_mentions))
    open_todo = random.randint(0, 500)
    solved_todo = random.randint(0, open_todo)
