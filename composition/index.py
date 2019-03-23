from typing import List
import requests


class Index:
    def __init__(self,
                 name,
                 last_price_url: str,
                 free_float_url: str,
                 divisor: float,
                 multiplier: float,
                 client: requests.Session):
        self.name = name
        self.last_price_url = last_price_url
        self.free_float_url = free_float_url
        self.divisor = divisor
        self.multiplier = multiplier
        self.constituents = self.get_constituents
        self.price = self.get_price

    def __hash__(self):
        return hash(self.name)

    def get_constituents(self):
        return

    def get_price(self):
        return

