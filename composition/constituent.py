from http import cookiejar
import requests
import bs4
from functional import seq


class CookieBlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Stock:
    _user_agent = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36"
    _free_float_by_name: dict = {
        "Berkshire Hathaway": 2023560123,
        "Cboe Global Markets": 89000000,
        "Constellation Brands": 158000000,
        "Dow Inc.": 690800000,
        "Twenty-First Century Fox Class A": 506000000
    }

    def __init__(self,
                 url,
                 edgar_url,
                 name,
                 ticker):
        self._client = requests.Session()
        self._client.cookies.set_policy(CookieBlockAll)
        self._client.headers = {
            'user-agent': self._user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.url = url
        self.edgar_url = edgar_url
        self.name = name
        self.ticker = ticker
        self.last_price = False
        self.free_float = False
        self.weight = False

    def __repr__(self):
        return "name:{0} last_price:{1} free_float:{2}".format(self.name, self.last_price, self.free_float)

    def to_dict(self):
        return {"name": self.name,
                "ticker": self.ticker,
                "free_float": self.free_float,
                "last_price": self.last_price,
                "weight": self.weight}

    def text_to_num(self, text):
        d = {
            'K': 3,
            'M': 6,
            'B': 9
        }
        if text[-1].upper() in d:
            num, magnitude = text[:-1], text[-1]
            return float(num) * 10 ** d[magnitude]
        else:
            print('error applying multipliers to float on stock ' + self.name)
            return float(text)

    # noinspection PyBroadException
    def get_price_and_float(self):
        r = self._client.get(self.url)
        if r.status_code != 200:
            print('error ' + r.headers)
            return
        print(self.name)
        print(self.url)
        soup = bs4.BeautifulSoup(r.content, 'lxml')

        if self.name in list(self._free_float_by_name.keys()):
            self.free_float = self._free_float_by_name[self.name]
        else:
            try:
                shares_statistics_table = (
                    seq(soup.find_all('h3')).filter(lambda header: header.text == 'Share Statistics').to_list()[
                        0]).nextSibling
                shares_float_text = (shares_statistics_table.find_all('tr'))[3].contents[1].text
                self.free_float = self.text_to_num(shares_float_text)
            except:
                self.free_float = None

        try:
            share_price_text = (soup.find('div', {'class': "My(6px) Pos(r) smartphone_Mt(6px)"})
                                .find('span', 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)').text)
            self.last_price = float(share_price_text.replace(',', ''))
        except:
            self.last_price = None

        return self

    def set_weight(self, total_floating_market_cap):
        self.weight = self.last_price * self.free_float / total_floating_market_cap
