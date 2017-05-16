# flake8: noqa
import re
import json
import uuid
import logging
import requests
import datetime
import dateparser
import facebook

from urllib import request, error as urllib_error
from urllib.parse import urlparse, urlunparse
from requests import HTTPError

from apiclient.discovery import build  # import from google-api-python-client
from bs4 import BeautifulSoup, ResultSet

from apps.mentions.models import Mention
from apps.mentions.utils.apifier import Apifier
from config.settings.common import (APIFIER, FACEBOOK_APP_ID,
                                    FACEBOOK_APP_SECRET)


logger = logging.getLogger(__name__)


class ParserNotFound(Exception): pass


class GoogleCustomSearchSDK(object):
    """
    Class to find data in certain sites.
    We should specify query string, developer key and search engine
    Attributes:
        service (service): service object to work with google API
        res: result of google custom search
    """

    def __init__(self, query, devKey, engine_cx):
        """
        Constructor
        Args:
            query (str):  Query to find in google
            devKey (str): google API dev key
                    (https://support.google.com/cloud/answer/6158857)
            engine_cx (str): code of custom search engine,
                       you've got it when engine was created
                        "customsearch" - type of API we use
                        "v1" - version of api
        filter (string), Controls turning on or off the
                        duplicate content filter.
                        Allowed values
                            0 - Turns off duplicate content filter.
                            1 - Turns on duplicate content filter.
        """
        self.service = build("customsearch", "v1", developerKey=devKey)
        self.res = self.service.cse().list(q=query, cx=engine_cx, filter='1', )

    def start_search(self):
        """
        Method to start google search
        Returns:
            google response
        """
        return self.res.execute()

    def get_values(self, search):
        """
        Method to extract values from search results
        Args:
            search: result of start_search function
        Returns:
            results (list): list of Mention objects with
                            filled corresponded fields
        """
        results = list()
        items = search.get('items')
        queries = search.get('queries')
        request = queries.get('request')
        searchTerms = request[0].get('searchTerms')
        if items:
            for item in items:
                try:
                    par = ParserFabric(item, searchTerms)
                    par.set_parser()
                    results.extend(par.get_results())
                except ParserNotFound as e:
                    logger.warning('Parser not found: {0}'.format(e))
                except:
                    logger.error('Parser error')
        return results


class CustomParser(object):
    """
    Base class to define custom parser for google results
    Attributes:
        parser (class): class of the parser
        results (list): list of results
        item (dict): one item from google response
        searchTerms (str): query which we ask from google
        page (dict): pagemap object from response
        link (str): url of certain mention
        date (datetime): date of mentions were made
        origin (str): part of url of origine sit something like www.yelp.com,
                      note: for google+ it will be plus.google.com
        snippet (str): text from snippet key from response
        reviews (dict): content of review tag from response
        blogposting (dict): content of blogposting tag from response
    """
    parser = None

    def __init__(self, item, searchTerms=None):
        self.results = list()
        self.item = item
        self.searchTerms = searchTerms
        self.page = item.get('pagemap')
        self.link = item.get('link')
        self.date = item.get('date')
        self.origin = item.get('displayLink')
        self.snippet = item.get('snippet')
        self.reviews = self.page.get('review')
        self.blogposting = self.page.get('blogposting')

    def create_mention(self, text='', date=None, author=''):
        """
        Method to create certain mention
        Args:
            author (str): mention author
            date (datetime): mention date
            text (str): mention text
        Returns:
            mention (Mention): mention object to be append to result list
        """
        mention = Mention(u_id=uuid.uuid4())
        mention.mention_text = text
        mention.mention_date = date
        mention.mention_author = author
        mention.mention_link = self.link
        mention.origin_site = self.origin
        return mention

    def get_results(self):
        """
        Method to call parse() from certain class
        Returns:
            (list): result of parse() method -list of Merchant instances
        """
        return self.parser.parse()


class ParserFabric(CustomParser):
    """Fabric to create parser for certain site.

    Contains a method for set parser for selected source.

    """

    def set_parser(self):
        """Set parser for a source.

        Set parser if exists, else raise exceprion 'ParserNotFount'.

        """
        parsers = {
            'plus.google.com': GooglePlusParser(self.item, self.searchTerms),
            'www.facebook.com': FacebookParser(self.item),
            'www.yelp.com': YelpParser(self.item),
            'www.bbb.org': BBBParser(self.item),
            'www.ripoffreport.com': RipOfReportParser(self.item)
        }

        try:
            self.parser = parsers[self.origin.lower()]
        except KeyError as e:
            raise ParserNotFound('Parser {0} not found'.format(e))


class YelpParser(CustomParser):
    """Parser for mentions from Yelp.

    Gets mention text, date and author. Creates list of mentions objects.

    """

    def parse(self):
        """Method to parse results.

        Returns:
          (list): list of Merchant instances.

        """
        html_doc = request.urlopen(self.link)
        soup = BeautifulSoup(html_doc, 'html5lib')
        reviews = soup.find_all('div', 'review')
        parse = dateparser.parse

        for review in reviews:
            content = []
            date_ = None
            author = ''
            date_holder = review.find('span', 'rating-qualifier')

            if date_holder:
                try:
                    date_ = parse(date_holder.find('meta').get('content'))
                except AttributeError:
                    try:
                        date_ = parse(date_holder.get_text().strip())
                    except AttributeError:
                        pass

            author_from_site = review.find('a', 'user-display-name')

            if author_from_site:
                author = author_from_site.contents[0]

            paragraphs = review.find('p') or []

            for paragraph in paragraphs:
                if isinstance(paragraph, str):
                    content.append(paragraph)

            text = ''.join(content)

            criterias_for_ignoring = [
                text.startswith('Start your review of'),
                text.startswith('Hey there trendsetter!')
            ]

            if text.strip() and not any(criterias_for_ignoring):
                mention = self.create_mention(text=text, date=date_,
                                              author=author)
                self.results.append(mention)

        return self.results


class RipOfReportParser(CustomParser):
    """
    Parser for mentions from BBB an RipOfReport
    """

    def parse(self):
        """
        Method to parse results
        Returns:
            (list): list of Merchant instances
        """
        req = request.Request(self.link, headers={'User-Agent': "Opera"})
        html_doc = request.urlopen(req)
        soup = BeautifulSoup(html_doc, 'html5lib')
        report = soup.find('div', 'report-content')
        head = soup.find('div', 'reportText')
        date = head.find_all('span')[0]
        text = ''
        post_date = dateparser.parse(date.contents[0].strip())
        author_text = ''
        author = head.find_all('li')[2]
        if author:
            for item in author.contents:
                if isinstance(item, str):
                    author_text += item.strip()
                    if author_text:
                        break
        if report:
            for item in report.contents:
                if isinstance(item, str):
                    text += item.strip()
                else:
                    text += item.get_text()
        mention = self.create_mention(text=text, date=post_date,
                                      author=author_text)
        self.results.append(mention)
        return self.results


class BBBParser(CustomParser):
    """Parser for mentions from BBB.

    Parser gets a printable page of company and extracts complaints HTML.

    """

    def parse(self):
        """Method to parse results.

        Returns:
          (list): list of Merchant instances.

        """
        parse = dateparser.parse
        results = ResultSet([])
        url_parts = urlparse(self.link)
        url_splitted_path = list(filter(None, url_parts.path.split('/')))
        stop_ends = ['complaints', 'customer-reviews', 'print']

        if url_splitted_path[len(url_splitted_path)-1] in stop_ends:
            url_splitted_path.pop()

        url_path = '/'.join(url_splitted_path + ['print'])

        url = urlunparse((url_parts.scheme, url_parts.netloc, url_path,
                          None, None, None))

        try:
            html_doc = request.urlopen(url)
        except urllib_error.HTTPError:
            logger.error('BBB parser failed with {0}'.format(self.link))
            raise

        soup = BeautifulSoup(html_doc, 'html.parser')

        try:
            results += soup.find(
                'table', 'cmpldetail'
            ).find_all(
                'tr', re.compile('odd|even')
            )
        except AttributeError:
            pass

        try:
            results += soup.find(
                'div', 'customer-complaint-summary'
            ).find_all(
                'tr', re.compile('odd|even')
            )
        except AttributeError:
            pass

        for result in results:
            try:
                date_ = parse(result.find('td', 'date').text)
                text = result.find('p').text or ''
                text = re.sub(r'^Complaint:|Complaint', '', text).strip()

                self.results.append(
                    self.create_mention(text=text, date=date_)
                )
            except AttributeError:
                continue
        
        return self.results


class FacebookParser(CustomParser):
    """
    Parser for mentions from Facebook
    """

    def parse(self):
        """
        Method to parse results
        Returns:
            (list): list of Merchant instances
        """
        page_url = urlparse(self.link)
        page_id = page_url.path.strip('/')
        # TODO change app_id and secret to client's ones
        token = facebook.GraphAPI().get_app_access_token(
            app_id=FACEBOOK_APP_ID, app_secret=FACEBOOK_APP_SECRET)
        graph = facebook.GraphAPI(access_token=token, version='2.5')
        try:
            feed = graph.get_connections(id=page_id,
                                         connection_name='feed')
            data = feed.get('data')
            for item in data:
                print(item)
                message = item.get('message')
                date = dateparser.parse(item.get('created_time'))
                if message and not urlparse(message).scheme:
                    mention = self.create_mention(text=message, date=date)
                    self.results.append(mention)
            if self.reviews:
                for review in self.reviews:
                    text = str()
                    # we try to get text
                    description = review.get('description')
                    reviewbody = review.get('reviewbody')
                    if description:
                        text = description
                    elif reviewbody:
                        text = reviewbody
                    mention = self.create_mention(text=text,
                                                  date=review.get(
                                                      'datepublished'),
                                                  author=review.get('author'))
                    self.results.append(mention)
        except facebook.GraphAPIError as e:
            logger.error(e)
        return self.results


class GooglePlusParser(CustomParser):
    """
    Parser for mentions from Google Plus
    """

    def parse(self):
        """
        Method to parse results
        Returns:
            (list): list of Merchant instances
        """
        max_results = 10
        # cut daterange from request due to API requirements
        daterange = self.searchTerms.find('daterange')
        query = self.searchTerms[0:daterange - 1]
        payload = {
            'query': query,
            'maxResults': max_results,
            'fields': 'items(actor/displayName,object/content,published)',
            'key': 'AIzaSyC-ZNseJBPdkWNww-tzca8SO4UmIyAuQdw'
        }
        response = requests.get('https://www.googleapis.com/plus/v1/activities',
                                params=payload)
        res = json.loads(response.content.decode('utf-8'))
        items = res.get('items')
        date, author, text = datetime.datetime, str(), str()
        if items:
            for item in items:
                published = item.get('published')
                if published:
                    date = dateparser.parse(published)
                else:
                    date = self.date
                actor = item.get('actor')
                if actor:
                    author = actor.get('displayName')
                object = item.get('object')
                if object:
                    content = object.get('content')
                    if content:
                        p = re.compile(r'<.*?>')
                        text = p.sub('', content)
                mention = self.create_mention(text=text, date=date,
                                              author=author)
                self.results.append(mention)
        return self.results
