import csv
import re

from collections import namedtuple, OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import (validate_email, URLValidator,
                                    ValidationError)

from localflavor.us.us_states import STATES_NORMALIZED

from apps.users.models import AppUser
from apps.mentions.models import Merchant, Category


class CustomCSValidator(object):
    """
    Class to define validator for merchant bulk import purposes
    Args:
        row (dict): row from parsed file
        index (int): index of the row in file
        merchants (list): list of validated merchants prepared to save
    Attributes:
        invalid_rows (list): list of lists with errors and warnings
        user (AppUser): user object, to check either exists or not
        merchant (Merchant): merchant object, to check either exists or not
        success (bool): flag if row valdated successfully or not
    """

    r_official_name = r'^[\w*\s*\D]{1,254}'
    r_zip_code = r'^\d{5}(?:-\d{4})?$'
    r_phone = r'^(?:1-?)?(\d{3})[-\.]?(\d{3})[-\.]?(\d{4})$'
    r_username = r'^[\w*]{3,16}$'
    r_password = r'^[\w*]{6,18}$'

    def __init__(self, row, index, merchants):
        """Constructor for CustomCSValidator"""
        self.data = row
        self.index = index
        self.merchants = merchants
        self.invalid_rows = list()
        self.user = None
        self.merchant = None
        self.success = True

    def __bool__(self):
        return self.success

    def set_message(self, message):
        self.invalid_rows.append(message)

    @property
    def official_name(self):
        return self.data.get('official_name', None)

    @property
    def state(self):
        return self.data.get('state', None)

    @property
    def zip_code(self):
        return self.data.get('zip_code', None)

    @property
    def sources(self):
        return self.data.get('sources', None)

    @property
    def phones(self):
        phones = OrderedDict()

        for i in range(3):
            if self.data.get('phone{}'.format(i)):
                phones.update((('phone{}'.format(i),
                                self.data.get('phone{}'.format(i))),))
        return phones

    @property
    def urls(self):
        urls = OrderedDict()

        for i in range(5):
            if self.data.get('web_page{}'.format(i)):
                urls.update(((
                    'web_page{}'.format(i),
                    self.data.get('web_page{}'.format(i))
                ),))

        return urls

    @property
    def industry_name(self):
        return self.data.get('industry_name', None)

    @property
    def user_email(self):
        return self.data.get('user_email', None)

    def _validate_name(self):
        """
        Method to validate merchant business name
        """
        # business name is required field, if not provided - reject this row
        if not self.official_name:
            self.set_message(('{}'.format(self.index),
                              'Official name is required',
                              'Error'))
            raise ValidationError('Official name is required')
        else:
            name = self.official_name.strip()
        # general validation by regexp
        match = re.match(self.r_official_name, name)
        if not match or match.end() < len(name):
            self.set_message(('{}'.format(self.index),
                              'Official name is invalid, it should '
                              'contain only unicode symbols, '
                              'length should be less '
                              'then 255 characters',
                              'Error'))
            raise ValidationError('Official name is invalid')
        # if this name already mentioned in current file - reject row
        flag = False
        for merch in self.merchants:
            if merch['official_name'] == name:
                self.set_message(('{}'.format(self.index),
                                  'Merchant {} already mentioned '
                                  'in this file'.
                                  format(name),
                                  'Error'))
                flag = True
        if flag:
            raise ValidationError('Merchant already mentioned')
        # if such merchant already exists in DB - get warning
        if name:
            try:
                self.merchant = Merchant.objects.get(
                    official_name__iexact=name)
                self.set_message(('{}'.format(self.index),
                                  'Merchant {} already exists and '
                                  'will be updated'.
                                  format(self.merchant.official_name),
                                  'Warning'))
            except ObjectDoesNotExist:
                self.merchant = None
        self.data['official_name'] = name

    def _validate_state(self):
        """
        Method to validate merchant state
        """
        state = self.state
        state = STATES_NORMALIZED.get(state.strip().lower())
        # if there was a fail - skip this row
        if not state:
            self.set_message(
                ('{}'.format(self.index), 'State is invalid format, '
                                          'use valide US state name',
                 'Warning'))
            state = ''
        self.data['state'] = state

    def _validate_zip(self):
        """
        Method to validate merchant zip code
        """
        if self.zip_code:
            zip_code = self.zip_code.strip()
            if not re.match(self.r_zip_code, zip_code):
                self.set_message(('{}'.format(self.index),
                                  'ZIP code should be 5 digits',
                                  'Warning'))
                zip_code = ''
            self.data['zip_code'] = zip_code

    def _validate_phone(self):
        """
        Method to validate merchant phone
        """
        for i, key in enumerate(self.phones):
            phone = self.phones[key].strip()
            if not re.match(self.r_phone, phone):
                self.set_message(('{}'.format(self.index),
                                  'phone number {} should be '
                                  'like XXX-XXX-XXXX'.format(i+1),
                                  'Warning'))
                phone = ''
            self.data[key] = phone

    def _validate_url(self):
        """
        Method to validate merchant url
        """
        url_validator = URLValidator()
        for i, key in enumerate(self.urls):
            url = self.urls[key].strip()
            try:
                url_validator(url)
            except ValidationError:
                self.set_message(('{}'.format(self.index),
                                  'Url {} is not valid, '
                                  'the pattern is http://www.site.com'.
                                  format(i+1), 'Warning'))
                url = ''
            self.data[key] = url

    def _validate_industry(self):
        """
        Method to validate merchant industry
        """
        if self.industry_name:
            industry_name = self.industry_name.strip().lower()
            try:
                db_category = Category.objects.filter(
                    name__iexact=industry_name)
                if not db_category and len(industry_name) == 4:
                    Category.objects.filter(code=industry_name)
            # if such kind of industry doesn't exists in DB, merchant will be
            # created with empty industry, get warning
            except ObjectDoesNotExist:
                self.set_message(('{}'.format(self.index),
                                  "Industry like {} doesn't exists".
                                  format(industry_name),
                                  'Warning'))
            self.data['industry_name'] = industry_name
        # warning if industry isn't specified
        else:
            self.set_message(('{}'.format(self.index),
                              "Industry has not been specified".
                              format(self.industry_name),
                              'Warning'))

    def _validate_user_email(self):
        """
        Method to validate user_email
        """
        flag = False
        if self.user_email:
            user_email = self.user_email.strip().lower()
            try:
                validate_email(user_email)
            except ValidationError:
                self.set_message(('{}'.format(self.index),
                                  'User email is incorrect', 'Error'))
                raise ValidationError('User email is incorrect')
            try:
                # if such user already exists - error
                email = AppUser.objects.filter(email__iexact=user_email)
                if email:
                    self.set_message(('{}'.format(self.index),
                                      'This email already exists',
                                      'Error'))
                    raise ValidationError('This email already exists')
            except ObjectDoesNotExist:
                pass
            self.data['user_email'] = user_email
        else:
            flag = True
        # check if we already mention this merchant or usernme in .csv
        for merch in self.merchants:
            if self.user_email:
                if self.user_email.strip().lower() in merch['user_email']:
                    flag = True
        if flag:
            self.set_message(('{}'.format(self.index),
                              'Email is required and should be unique.',
                              'Error'))
            raise ValidationError('Username or email is already')

    def _validate_sources(self):
        DEFAULT_SOURCES = Merchant.SOURCES_LIST

        if self.sources:
            sources = [s.strip() for s in self.sources.split(',')]

            self.data['sources'] = list(set(sources) & set(DEFAULT_SOURCES))
        else:
            self.data['sources'] = DEFAULT_SOURCES

    def apply_validators(self):
        """
        Method to apply all validators one by one
        """
        for attr in dir(self):
            if '_validate_' in attr:
                validator = getattr(self, attr)
                try:
                    validator()
                except ValidationError:
                    self.success = False
                    return False
        return True


def parse_merchants_csv(opened_file):
    """Function for parsing .csv file with list of merchants

    File should have following structure:
    First row - headers of columns
    The goes rows with info about merchants
    Args:
        opened_file (file): opened .csv file with info about merchants
    Returns:
        parser (namedtuple):
            merchants (list): parsed merchants with keys:
            invalid_rows (list): validation errors in following format:
                                    (row, message, level)
    """
    reader = csv.DictReader(
        opened_file,
        fieldnames=[
            'official_name', 'short_name0',
            'short_name1', 'short_name2',
            'address', 'city', 'state', 'zip_code',
            'location0', 'location1', 'location2', 'location3',
            'contact_info', 'phone0', 'phone1', 'phone2',
            'product0', 'product1', 'product2',
            'web_page0', 'web_page1', 'web_page2',
            'web_page3', 'web_page4',
            'ceo0', 'ceo1', 'ceo2',
            'dda', 'industry_name',
            'user_email', 'sources'
        ]
    )
    merchants = list()
    invalid_rows = list()

    for i, row in enumerate(reader):
        if reader.line_num == 1:
            continue

        validator = CustomCSValidator(row, i, merchants)
        validator.apply_validators()

        if validator:
            merchants.append(validator.data)
            invalid_rows.extend(validator.invalid_rows)
        else:
            invalid_rows.extend(validator.invalid_rows)

    parser = namedtuple('parser', ('merchants', 'invalid_rows'))

    return parser(merchants=merchants, invalid_rows=invalid_rows)
