from typing import List
from composition.constituent import Stock
from functional import pseq
import requests
import bs4


class Index:
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
        self.init_constituents()
        self.price = self.calculate_index()

    def __hash__(self):
        return hash(self.name)

    def init_constituents(self):
        self.get_constituents()
        self.get_constituent_prices_and_free_float()

    @staticmethod
    def calculate_index():
        return False

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
                Stock(
                    url=self.free_float_url.format(ticker),
                    edgar_url=edgar_url,
                    name=name
                )
            )

    def get_constituent_prices_and_free_float(self):
        #  https://www.investing.com/indices/investing.com-us-500-components would be cleaner
        #  but this is more about getting constituents and url above does not have them all.
        (pseq(self.components, processes=4, partition_size=130)
         .map(lambda stock: stock.get_price_and_float())
         .to_list())
