import datetime
from http import cookiejar
import requests
import bs4
from functional import seq


def text_to_num(text):
    d = {
        'M': 6,
        'B': 9
    }
    if text[-1] in d:
        num, magnitude = text[:-1], text[-1]
        return float(num) * 10 ** d[magnitude]
    else:
        print('error applying multipliers to float')
        return float(text)


class CookieBlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Stock:
    _user_agent = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36"

    def __init__(self,
                 url,
                 edgar_url,
                 name):
        self._client = requests.Session()
        self._client.cookies.set_policy(CookieBlockAll)
        self._client.headers = {
            'user-agent': self._user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.url = url
        self.edgar_url = edgar_url
        self.name = name
        self.last_price = False
        self.free_float = False

    def __repr__(self):
        return "name:{0} last_price:{1}".format(self.name, self.last_price)

    # noinspection PyBroadException
    def get_price_and_float(self):
        r = self._client.get(self.url)
        if r.status_code != 200:
            print('error ' + r.headers)
            return
        print(self.name)
        print(self.url)
        soup = bs4.BeautifulSoup(r.content, 'lxml')

        try:
            shares_statistics_table = (seq(soup.find_all('h3')).filter(lambda header: header.text == 'Share Statistics').to_list()[0]).nextSibling
            shares_float_text = (shares_statistics_table.find_all('tr'))[3].contents[1].text
            self.free_float = text_to_num(shares_float_text)
        except:
            self.free_float = None

        try:
            share_price_text = (soup.find('div', {'class':"My(6px) Pos(r) smartphone_Mt(6px)"})
                                .find('span', 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)').text)
            self.last_price = float(share_price_text)
        except:
            self.last_price = None

        print('{0} price is {1} float is {2} @ {3}'.format(
            self.name,
            self.last_price,
            self.free_float,
            datetime.datetime.now().strftime("%H:%M:%S")))

    def get_free_float(self):
        self.free_float = 1.0
