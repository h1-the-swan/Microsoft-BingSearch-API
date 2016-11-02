import sys, os, warnings, requests

MICROSOFT_BING_SEARCH_KEY = os.environ.get('MICROSOFT_BING_SEARCH_KEY') or ''
if not MICROSOFT_BING_SEARCH_KEY:
    warnings.warn('MICROSOFT_BING_SEARCH_KEY not set in environment')

api_request_header = {
        'Ocp-Apim-Subscription-Key': MICROSOFT_BING_SEARCH_KEY
        }

img_search_url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'

class MicrosoftBingSearch(object):

    """Interact with Microsoft Bing Search API"""

    def __init__(self, **kwargs):
        """TODO: to be defined1. """
        self.header = api_request_header
        self.img_search_url = img_search_url
        self.current_query = ""
        self.current_offset = 0
        self.query_threshold = kwargs.get('query_threshold')
        if not self.query_threshold:
            self.query_threshold = 1000
        self._number_of_queries = 0

    @property
    def number_of_queries(self):
        return self._number_of_queries

    @number_of_queries.setter
    def number_of_queries(self, value):
        if value > self.query_threshold:
            # too many queries
            raise RuntimeError("This instance has made {} queries. No more queries allowed".format(self.query_threshold))
        else:
            self._number_of_queries = value


    def get_img_search_response(self, query='', count=1, offset=0, safeSearch=None):
        """Make a request to the image search API and return a response

        :query: text query to be passed to the requests module
        :count: number of responses to return (default: 1)
        :offset: offset value for pagination of responses (default: 0)
        :returns: response dictionary (from requests.json())

        """
        params = {
                    'q': query,
                    'count': count,
                    'offset': offset,
                }
        if safeSearch:
            params['safeSearch'] = safeSearch
        self.number_of_queries += 1
        r = requests.get(self.img_search_url, params=params, headers=self.header)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 403:
            # exceeded queries per month limit
            return False
        elif r.status_code == 429:
            # exceeded queries per second limit
            return False
        else:
            # something else went wrong
            return False

    def get_single_img_url(self, query):
        """Given a query, get the first image url returned by Bing

        :query: query string
        :returns: image url

        """
        if not query:
            return ""
        if query == self.current_query:
            self.current_offset += 1
        else:
            self.current_offset = 0
            self.current_query = query
        r = self.get_img_search_response(query, offset=self.current_offset)
        if r['value']:
            bing_url = r['value'][0]['contentUrl']
            # use requests to resolve redirect
            imgr = requests.get(bing_url)
            if imgr.status_code == 200:
                return imgr.url
            else:
                return ""
        else:
            # empty result
            return ""

    def get_multiple_img_url(self, query, count=10):
        """Given a query, get the first image url returned by Bing

        :query: query string
        :count: number of results (default: 10)
        :returns: image url

        """
        if not query:
            return []
        # if query == self.current_query:
        #     self.current_offset += 1
        # else:
        #     self.current_offset = 0
        #     self.current_query = query
        r = self.get_img_search_response(query, count=count)
        if r['value']:
            urls = []
            for item in r['value']:
                bing_url = item['contentUrl']
                # use requests to resolve redirect
                imgr = requests.get(bing_url)
                if imgr.status_code == 200:
                    urls.append(imgr.url)
            return urls
        else:
            # empty result
            return []
