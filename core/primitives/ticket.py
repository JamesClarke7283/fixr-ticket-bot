from .event import Event
from selenium import webdriver


class Ticket:
    def __init__(self, driver: webdriver, name: str, price: float, event: Event, web_element=None):
        self.driver = driver
        self.name = name
        self.price = price
        self.web_element = web_element
        self.event = event

    def __repr__(self):
        return f"{self.name} - £{self.price}"

    def buy(self, amount=1):
        raise NotImplementedError


class TicketList:
    def __init__(self, driver: webdriver, event: Event):
        self.driver = driver
        self.tickets: list[Ticket] = []

    def filter_by_exclude_keywords(self, keywords: list[str]) -> list[Ticket]:
        """Returns a list of tickets that do not contain any of the keywords"""
        return [t for t in self.tickets if t.name not in keywords]

    def filter_by_budget(self, max_price: float, min_price: float = 0) -> list[Ticket]:
        """Returns a list of tickets that are less than or equal to the max price"""
        return [t for t in self.tickets if t.price <= max_price and t.price >= min_price]
