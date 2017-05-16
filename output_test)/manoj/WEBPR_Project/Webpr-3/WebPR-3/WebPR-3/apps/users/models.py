from django.contrib.auth.models import AbstractUser
from django.db import models
from imagekit import models as imagekitmodels
from imagekit.processors import ResizeToFill
from libs import utils


def upload_user_media_to(instance, filename):
    """Upload media files to this folder"""
    return '{}/{}/{}'.format(instance.__class__.__name__.lower(), instance.id,
                             utils.get_random_filename(filename))


class Account(models.Model):
    """
    Base entity which define users, prising plan, track list and so on.
    All users belongs to some account as well as merchant.
    Attributes:
        company_name (str): name of account
        type (str): ISO or merchant
        plan (int): pricing plan - currently not in use,
                                just for future functionality
        merchant (Merchant): FK to merchants who linked with this account
        is_active (bool): is account active
    """
    ISO = "i"
    MERCHANT = "m"
    _ACCOUNT_TYPES = (
        (ISO, 'ISO'),
        (MERCHANT, 'Merchant'))

    _PRICING_PLANS = ((0, 'Simple'), (1, 'Advanced'))

    company_name = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(choices=_ACCOUNT_TYPES, max_length=1, blank=True,
                            null=True)
    plan = models.PositiveSmallIntegerField(choices=_PRICING_PLANS, blank=True,
                                            null=True)
    merchants = models.ManyToManyField('mentions.Merchant',
                                       blank=True, db_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ('company_name',)
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'


class AppUser(AbstractUser):
    """
    User of an application, inherited from django user
    Attributes:
        account (Account): FK to account
        role (int): role of user: admin or usual user
        avatar (image): user avatar
    """
    ADMIN_ROLE = 'a'
    USER_ROLE = 'u'
    ROLES = (
        (ADMIN_ROLE, 'Admin'),
        (USER_ROLE, 'User'))

    account = models.ForeignKey(Account, related_name='users',
                                blank=True, null=True, db_index=True)
    role = models.CharField(max_length=1, choices=ROLES, blank=True,
                            null=True)

    # avatar
    avatar = imagekitmodels.ProcessedImageField(
        upload_to=upload_user_media_to, processors=[ResizeToFill(40, 40)],
        format='PNG', options={'quality': 100},
        null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return "{} {}".format(self.first_name.capitalize(),
                              self.last_name.capitalize())

    @property
    def is_merchant(self):
        """Is current user is merchant account
        """
        return self.account.type == Account.MERCHANT

    @property
    def is_iso(self):
        """Is current user is ISO account
        """
        return self.account.type == Account.ISO

    @property
    def is_iso_admin(self):
        """Is current user is admin for ISO
        """
        return self.is_iso and self.role == AppUser.ADMIN_ROLE


class APIKey(models.Model):
    """
    Table to persist key from third-party services
    Attributes:
        account (Account): FK to account
        token (str): token or somthing else
        secret (str): secret or something else
        api_type (int): type of third-party service

    """
    GOOGLE = 'g'
    SEMANTRIA = 's'
    _API_TYPE = ((GOOGLE, 'Google'), (SEMANTRIA, 'Semantria'))
    account = models.ManyToManyField(Account, blank=True, db_index=True)
    token = models.CharField(max_length=255)
    secret = models.CharField(max_length=255, blank=True, null=True)
    api_type = models.CharField(max_length=1, choices=_API_TYPE)

    class Meta:
        index_together = ('api_type', 'token', 'secret')

    def __str__(self):
        return self.token
