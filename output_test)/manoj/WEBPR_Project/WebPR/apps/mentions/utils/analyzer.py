"""
Facade implementation for crawling and sentiment analysis
"""
import logging

from itertools import zip_longest
from operator import attrgetter

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from requests import HTTPError
from jdcal import gcal2jd

from apps.users.models import APIKey
from apps.mentions.models import TemporaryResults
from apps.mentions.utils.google_sdk import GoogleCustomSearchSDK
from apps.mentions.utils.semantria_analyser import SemantraAnalyzer
from config.settings.common.business_logic import SEARCH_PERIOD

logger = logging.getLogger(__name__)


class GoogleCrawler(object):
    """
    Google crawler class
    you should specify:
     1) account id to search for,
     2) merchant instance
     Token and secret will be received from DB automatically
    Attributes:
        acc_id (int): id of account
        merchant (Merchant): merchant instance
        token (str):  token for google service
        secret (str): engine id for google service
    """

    def __init__(self, acc_id, merchant, token=None, secret=None):
        self.acc_id = acc_id
        self.merchant = merchant
        self.token = token
        self.secret = secret

    def get_credentials(self):
        """
        Get credentials for crawling API from DB
        """
        try:
            credentials = APIKey.objects.get(account=self.acc_id,
                                             api_type=APIKey.GOOGLE)
            self.token = credentials.token
            self.secret = credentials.secret
        except ObjectDoesNotExist:
            credentials = APIKey.objects.filter(api_type=APIKey.GOOGLE).first()
            self.token = credentials.token
            self.secret = credentials.secret

    @staticmethod
    def get_query_string(merchant, field_name):
        """Get Google search query string for field(s).

        The method makes query string for field or more fields (if array) and
        concatenates with ``OR`` if ``use_or_prefix`` is True

        Args:
          merchant (object): An instance of ``Merchant``.
          field_name (string): Name of the field, for which will make query.
          use_or_prefix (bool): If True -- add prefix for ``OR`` condition.

        Returns:
          Empty string or result query for search.

        """

        def get_filtered(value):
            assert type(value) in (list, str)

            if isinstance(value, list):
                return [x.strip() for x in value if x.strip()]
            return [value.strip()]

        def prepare(terms_list):
            keyword, quoted = terms_list

            if quoted:
                return '"{0}"'.format(keyword)
            return keyword

        fieldnamegetter = attrgetter(field_name)
        search_settings = merchant.search_settings or {}
        field_settings = search_settings.get(field_name, [])
        values = get_filtered(fieldnamegetter(merchant))
        prefix = '' if field_name == 'official_name' else 'OR '
        query = []

        for value in zip_longest(values, field_settings, fillvalue=False):
            query.append('{0}{1}'.format(prefix, prepare(value)))

        return ' '.join(query) if query else ''

    @staticmethod
    def create_query(merchant):
        """Create search query for Google.

        The function creates query string according to google search language,
        uses Official name, Alt business names, products and excluding words.

        Args:
          merchant (object): An instance of Merchant class.

        Returns (str):
          String to make query for google.

        """
        fields = ('official_name', 'short_name', 'product')
        query = []

        for field in fields:
            query.append(GoogleCrawler.get_query_string(merchant, field))

        if merchant.exclude_words:
            exclude_words = [
                word.strip() for word
                in merchant.exclude_words.split(',')
                if word.strip()
            ]

            for word in exclude_words:
                query.append('-"{0}"'.format(word))

        # should be in Julian date format
        period = SEARCH_PERIOD
        date = timezone.now()
        jul_date = gcal2jd(date.year, date.month, date.day)
        start_date = jul_date[0] + jul_date[1] + 0.5

        query.append('daterange:{0}-{1}'.format(str(start_date), str(period)))

        return ' '.join(query)

    def start_search(self):
        """Call the Google SDK.

        Returns:
          result_list (list): list of texts for analysis

        """
        self.get_credentials()
        query = self.create_query(merchant=self.merchant)

        try:
            g_search = GoogleCustomSearchSDK(query, self.token, self.secret)
            google_responce = g_search.start_search()
            # create record to store google response during 33 days
            TemporaryResults.objects.create(merchant=self.merchant,
                                            google_responce=google_responce)
            result_list = g_search.get_values(google_responce)
            return result_list
        except HTTPError:
            logger.error('HTTP error')


class Sentiment(object):
    """
    In case of separated API it will be the adapter for sentiment analysis
    Attributes:
        acc_id (int): account id
        mentions (dict): dictionary with mentions from DB
        token (str): access token for db
        secret (str): semantria secret
    """

    def __init__(self, acc_id, mentions=None, token=None, secret=None):
        self.acc_id = acc_id
        self.mentions = mentions
        self.token = token
        self.secret = secret

    def get_credentials(self):
        """
        Get credentials for sentiment API from DB
        """
        try:
            credentials = APIKey.objects.get(account=self.acc_id,
                                             api_type=APIKey.SEMANTRIA)
            self.token = credentials.token
            self.secret = credentials.secret
        except ObjectDoesNotExist:
            credentials = APIKey.objects.filter(
                api_type=APIKey.SEMANTRIA).first()
            self.token = credentials.token
            self.secret = credentials.secret

    def start_sentiment(self):
        """
        Launch of the sentiment analyzer
        Returns:
             list of sentiment results: text and positive/negative/neutral tag
        """
        self.get_credentials()
        sentim_analyzer = SemantraAnalyzer(self.token, self.secret)
        analysis_res = sentim_analyzer.semant(self.mentions)
        TemporaryResults.objects.create(semantria_responce=analysis_res)
        return analysis_res


class BaseAnalyzer(object):
    """
    Facade for third-party APIs
    Attributes:
        acc_id (int): account id
        merchant: the instance of Merchant class
        _crawler: Crawler to find mentions (Google in first phase)
        _sentiment: sentiment analyser (semantria in first phase)
        mentions (list): list of mentions to be analysed
    """

    CRAWLER = None
    ANALYZER = None

    def __init__(self, account_id, merchant):
        self.acc_id = account_id
        self.merchant = merchant
        self._crawler = self.CRAWLER(self.acc_id, self.merchant)
        self._sentiment = self.ANALYZER(self.acc_id)

    def crawl(self):
        """
        Function to start crawling
        Returns:
            mentions (list): list of mentions to be analysed
        """
        return self._crawler.start_search()

    def analyze(self, mentions):
        """
        Function to start analysis
        Args:
            mentions (list): list of mentions to be analysed
        Returns:
            mentions (list): list of mentions after analysis
        """
        self._sentiment.mentions = mentions
        print(self._sentiment)
        return self._sentiment.start_sentiment()


class Analyzer(BaseAnalyzer):
    """
    Class to be called from client's code
    Attributes:
        CRAWLER (class): class for search mentions
        ANALYZER (class): class for mentions analysis
    """
    CRAWLER = GoogleCrawler
    ANALYZER = Sentiment
