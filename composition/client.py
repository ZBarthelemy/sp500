from functional import seq

from composition.index import Index
from http import cookiejar
import requests
import pandas


class CookieBlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Client(object):
    _user_agent = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36"
    _index_specs = {
        'sp500': {'constituents': "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                  'float': "https://finance.yahoo.com/quote/{0}/key-statistics?p={0}",
                  'divisor': 8.9e9,
                  'multiplier': 1
                  }
    }

    def __init__(self):
        self._client = requests.Session()
        self._client.cookies.set_policy(CookieBlockAll)
        self._client.headers = {
            'user-agent': self._user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }

    def get_index(self, name):
        index_specs = self._index_specs[name]
        # noinspection PyTypeChecker
        return Index(name='S&P500',
                     constituents_url=index_specs['constituents'],
                     free_float_url=index_specs['float'],
                     divisor=index_specs['divisor'],
                     multiplier=index_specs['multiplier'],
                     client=self._client)


c = Client()
spx: Index = c.get_index(name='sp500')
current_components = spx.components
json = (seq(current_components)
        .map(lambda s: s.to_dict())
        .to_list())
df = pandas.DataFrame(json)[["name", "free_float", "last_price", "edgar_url"]]
df.to_csv(r"/Users/whitestallion/Desktop/sp500shit.csv")
print('done')
