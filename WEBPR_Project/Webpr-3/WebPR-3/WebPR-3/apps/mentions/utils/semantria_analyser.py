"""
We use Semantria SDK for Python.
The code is using as-is, without any changes.
Source is in apps/mentions/utils/semantria.
URL to GitHub: https://github.com/Semantria/semantria-sdk
"""
import logging
from collections import namedtuple
from apps.mentions.utils.semantria import jsonserializer, session
from django.conf import settings

logger = logging.getLogger(__name__)


def chunk(lst, count):
    """
    Function to return slices from list
    Args:
        lst (list): list to slice
        count (int): how much elements in slice should be
    Returns:
        generator object
    """
    start = 0
    for i in range(count):
        stop = start + len(lst[i::count])
        yield lst[start:stop]
        start = stop


class SemantraAnalyzer(object):
    """
    Class to work with Semantria API
    We should provide proper token and secret to make sentiment analysis of
    mentions. Token and secret are stored in DB.
    """

    def __init__(self, token, secret):
        self.token = token
        self.secret = secret

    def put_sentiment_queue(self, session, data):
        """
        function to put texts into cloud queue for analysis
        Args:
            session (Session): semantria session
            data (list): list of texts to be analysed
        Returns:
            statuses (list): list of statuses which describes sentiment
                             analysis results
        """
        statuses = []
        batch = []
        for mention in data:
            doc = {
                'id': str(mention.u_id).replace('-', ''),
                'text': mention.mention_text[0:255]
            }
            batch.append(doc)
        try:
            semantria_conf_id = settings.SEMANTRIA_CONF_ID

            if batch and len(batch) < 100:
                status = session.queueBatch(
                    batch=batch,
                    config_id=semantria_conf_id
                )
                statuses.append(status)
                return statuses
            elif batch:
                batches = list(chunk(batch, 100))
                for b in batches:
                    status = session.queueBatch(
                        batch=b,
                        config_id=semantria_conf_id
                    )
                    statuses.append(status)
                return statuses
        except TypeError:
            statuses.append('No results to analyse')
        finally:
            return statuses

    def match_mentions(self, mention, sentiment):
        """
            function to compare id from search results and sentiment results,
            if match then add polarity and sentiment value
            Args:
                mention (Mention): mentions from db to update
                sentiment (dict): mentions from sentiment analysis
            Returns:
                mention (dict): mentions from db to update after matching
                sentiment (dict): mentions from sentiment analysis
                                    after matching
            """
        print(mention.u_id, sentiment.get('u_id'))
        i = 0
        if mention.u_id == sentiment.get('u_id'):
            mention.sentiment = sentiment['sentiment']
            mention.sentiment_value = sentiment['sentiment_value']
            print(i)
            i += 1
        match_mentions = namedtuple('match_mentions', ('mention', 'sentiment'))
        return match_mentions(mention=mention, sentiment=sentiment)

    def get_sentiment_stauses(self, session, comments):
        """
        function to retrieve analysis stauses from cloud queue
        Args:
            comments (list): list of strings to analyse
            session (local_session): semantria session
        Returns:
            stauts (semantria status): list of statuses of sentiment analysis
        """
        results = []

        # get processed documents
        status = session.getProcessedDocuments()
        if status:
            results.extend(status)
        return results

    def get_sentiment_results(self, session, comments):
        """
        function to retrieve analysis results from cloud queue
        Args:
            comments (list): list of strings to analyse
            session (session): semantria session
        Returns:
            mentionsSentiment (list): list of results of sentiment analysis
        """
        try:
            results = self.get_sentiment_stauses(session, comments)
            mentionsSentiment = []
            for result in results:
                sentiment = {'sentiment': result.get('sentiment_polarity'),
                             'mention_text': result.get('summary'),
                             'sentiment_value': result.get('sentiment_score'),
                             'u_id': result.get('id')}
                # for mention in comments:
                # mention, sentiment = self.match_mentions(mention, sentiment)
                mentionsSentiment.append(sentiment)
            return mentionsSentiment
        except TypeError:
            logger.error("object of type 'NoneType' has no len()")

    def semant(self, mentions):
        """
        method to provide sentiment analysis
        we should sequentially make json serializer, create session,
        put mentions into queue and finally retrive results from analysis
        Args:
            mentions (list): mentions to analyse
        Returns:
            length of mentions list
        """
        # start semantria session
        serializer = jsonserializer.JsonSerializer()

        _session = session.Session(self.token, self.secret, serializer,
                                   use_compression=True)

        self.put_sentiment_queue(_session, mentions)
        return len(mentions)
