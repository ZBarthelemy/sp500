from typing import List
from composition.constituent import Stock
from functional import pseq, seq
import requests
import bs4


class Index:

    _spx_constituent_to_remove = ["Alphabet Inc Class A",
                                  "News Corp. Class A",
                                  "Twenty-First Century Fox Class B"]

    def __init__(self,
                 name,
                 constituents_url: str,
                 free_float_url: str,
                 divisor: float,
                 multiplier: float,
                 client: requests.Session):
        self._client = client
        self.components: List[Stock] = []  # len is 5 larger due to dual class listings
        self.name = name
        self.constituents_url = constituents_url
        self.free_float_url = free_float_url
        self.divisor = divisor
        self.multiplier = multiplier
        self.price = None
        self.init_constituents()
        self.filter_dual_and_set_weights()

    def __hash__(self):
        return hash(self.name)

    def init_constituents(self):
        self.get_constituents()
        self.get_constituent_prices_and_free_float()

    def filter_dual_and_set_weights(self):
        index_free_float_mkt_cap = 0.0
        self.components = list(filter(lambda s: s.name not in self._spx_constituent_to_remove, self.components))
        for instrument in self.components:
            index_free_float_mkt_cap += instrument.last_price * instrument.free_float
        for stock in self.components:
            stock.set_weight(index_free_float_mkt_cap)
        self.price = index_free_float_mkt_cap / self.divisor * self.multiplier

    def get_constituents(self):
        r = self._client.get(self.constituents_url)
        if r.status_code != 200:
            return
        wiki_soup = bs4.BeautifulSoup(r.content, 'lxml')
        table = wiki_soup.find('table', {'class': 'wikitable sortable'})
        for row in table.findAll('tr')[1:]:
            columns = row.findAll('td')
            name = columns[0].text
            ticker = str.replace(columns[1].text, '.', '-')
            edgar_url = columns[2].next_element.get('href')
            self.components.append(
                Stock(url=self.free_float_url.format(ticker),
                      edgar_url=edgar_url,
                      name=name,
                      ticker=ticker.replace('-', '')
                )
            )

    def get_constituent_prices_and_free_float(self):
        self.components = (pseq(self.components, processes=4, partition_size=130)
                           .map(lambda stock: stock.get_price_and_float())
                           .to_list())
