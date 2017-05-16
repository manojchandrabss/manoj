import json
import requests
import time
import logging
import re
# from timeit import default_timer
# from config.settings.common import APIFIER

logger = logging.getLogger(__name__)


class Apifier(object):
    """
    Class for itreaction with Apifier API
    """

    def __init__(self, crawler, bbb_url):
        self.crawler = crawler
        self.bbb_url = bbb_url

    def _set(self):
        """
        Method to set request to the Apifier
        Returns:
            responce (json): responce from apifier
        """
        try:

            payload = {"startUrls": [{"key": "BBB", "value": self.bbb_url}]}
            responce = requests.post(url=self.crawler,
                                     json=payload)
            print(responce.json())
            return responce
        except Exception as e:
            logger.error("Fail to set settings to apifier with {}".format(e))

    def _run(self):
        """
        run the Apifier to get results
        Returns:
            json if success or status code if fail
        """
        run = self._set()
        if run.status_code == 200:
            return json.loads(run.content.decode("utf-8"))
        else:
            return run.status_code

    def retrieve(self):
        """
        Methid to retrive result from Apifier server
        Returns:
           content (list): list of results to be parsed
        """
        content = list()
        response = self._run()
        if isinstance(response, int):
            raise requests.HTTPError()
        else:
            link = response.get('resultsUrl')
            time.sleep(60)
            result = requests.get(link)
            if result.status_code == 200:
                page = json.loads(result.content.decode("utf-8"))
                for item in page:
                    pageFunctionResult = item.get('pageFunctionResult')
                    if pageFunctionResult:
                        content.append(pageFunctionResult)
        return content

    def parse(self, content):
        """
        Method to parse results from server
        Args:
            content (list): list of results to be parsed

        Returns:
            result (list): list of tuples with dates and texts of each result
        """
        result = list()
        texts = list()
        dates = list()
        p = re.compile(r'<.*?>')
        for item in content:
            for text in item.get('texts').values():
                texts.append(p.sub('', text))
            for date in item.get('dates').values():
                dates.append(p.sub('', date))
        result = list(zip(dates, texts))
        return result

# just for debugging:

# LINK_BBB = ('http://www.bbb.org/central-western-massachusetts/'
#             'business-reviews/auto-dealers-new-cars/'
#             'cargill-chevrolet-in-putnam-ct-102448')
#
#
# def new_BBB(link):
#     api = Apifier(
#         crawler=('https://api.apifier.com/v1/cmQCmosJAd2eB5FBz/crawlers/'
#                  'BBB/execute?token=mg64qiPcA5fxsbrgMSsgX4hhE'),
#         bbb_url=link)
#     results = dict()
#     try:
#         content = api.retrieve()
#         results = api.parse(content)
#     except Exception as e:
#         print(e)
#     return results
#
# if __name__ == '__main__':
#
#     res = new_BBB(LINK_BBB)
#     print(res)
#     # rip_parser(LINK_ROR)
#     # yelp_parser(LINK_YELP)
