from typing import List, Dict
from composition.constituent import Stock
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
        self.components: Dict[Stock] = {}
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
        self.intialize_constituents()

    @staticmethod
    def calculate_index():
        return False

    def get_constituents(self):
        r = self._client.get(self.constituents_url)
        wiki_soup = bs4.BeautifulSoup(r.content)
        return True

    def intialize_constituents(self):
        return
